type StartupSplashProps = {
  progress: number;
  step: string;
};

export function StartupSplash({ progress, step }: StartupSplashProps) {
  return (
    <main className="startup-screen">
      <section>
        <div className="brand-mark">FL</div>
        <h1>FLIFE Lite</h1>
        <p>{step}</p>
        <div className="startup-bar">
          <span style={{ width: `${progress}%` }} />
        </div>
      </section>
    </main>
  );
}
