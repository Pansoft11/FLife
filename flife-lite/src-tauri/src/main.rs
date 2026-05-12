use serde_json::{json, Value};
use std::fs::{create_dir_all, OpenOptions};
use std::io::Write;
use std::panic;
use std::path::PathBuf;
use std::process::Command;
use tauri::Manager;

#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("Python command failed: {0}")]
    Python(String),
    #[error("Invalid JSON response: {0}")]
    Json(String),
}

impl serde::Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::ser::Serializer,
    {
        serializer.serialize_str(&self.to_string())
    }
}

#[tauri::command]
fn run_analysis(app: tauri::AppHandle, settings: Value, material: Value) -> Result<Value, AppError> {
    let payload = json!({
        "settings": settings,
        "material": material,
        "samplingInterval": 0.0005
    });
    let output = run_python(&app, &["-m", "flife_lite_engine.cli", "--request-json", &payload.to_string()])?;
    let engine: Value = serde_json::from_str(&output).map_err(|err| AppError::Json(err.to_string()))?;
    Ok(json!({
        "lifeSeconds": engine["life_seconds"],
        "damagePerSecond": engine["damage_per_second"],
        "peakStressMpa": engine["peak_stress_mpa"],
        "rmsStressMpa": engine["rms_stress_mpa"],
        "cycles": engine["cycles"],
        "snCurve": engine["sn_curve"]
    }))
}

#[tauri::command]
fn license_status(app: tauri::AppHandle) -> Result<Value, AppError> {
    let output = run_python(&app, &["-m", "licensing.local_license.cli", "status"])?;
    serde_json::from_str(&output).map_err(|err| AppError::Json(err.to_string()))
}

#[tauri::command]
fn activate_license(app: tauri::AppHandle, email: String, license_key: String) -> Result<Value, AppError> {
    let output = run_python(&app, &["-m", "licensing.local_license.cli", "activate", "--email", &email, "--license-key", &license_key])?;
    serde_json::from_str(&output).map_err(|err| AppError::Json(err.to_string()))
}

fn run_python(app: &tauri::AppHandle, args: &[&str]) -> Result<String, AppError> {
    let root = app.path().resolve("..", tauri::path::BaseDirectory::Resource).unwrap_or_else(|_| {
        std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."))
    });
    let python_engine = root.join("python_engine");
    let app_src = root.join("src");
    let repository_root = root.parent().map(PathBuf::from).unwrap_or(root.clone());

    let python_path = [python_engine, app_src, repository_root]
        .iter()
        .map(|path| path.to_string_lossy().to_string())
        .collect::<Vec<_>>()
        .join(";");

    let output = Command::new("python")
        .args(args)
        .env("PYTHONPATH", python_path)
        .output()
        .map_err(|err| AppError::Python(err.to_string()))?;

    if !output.status.success() {
        return Err(AppError::Python(String::from_utf8_lossy(&output.stderr).to_string()));
    }
    Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
}

fn main() {
    panic::set_hook(Box::new(|info| {
        let base = std::env::var("LOCALAPPDATA").unwrap_or_else(|_| ".".to_string());
        let crash_dir = PathBuf::from(base).join("FLIFE").join("crash-dumps");
        let _ = create_dir_all(&crash_dir);
        let crash_file = crash_dir.join("flife-lite-rust-panic.log");
        if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(crash_file) {
            let _ = writeln!(file, "{:?}", info);
        }
    }));

    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![run_analysis, license_status, activate_license])
        .setup(|app| {
            if let Some(window) = app.get_webview_window("main") {
                window.show()?;
                window.set_focus()?;
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running FLIFE Lite");
}
