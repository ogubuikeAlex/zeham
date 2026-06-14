export function PageHeader({ eyebrow, title, children }: { eyebrow: string; title: string; children?: React.ReactNode }) {
  return (
    <section className="mesh-band border-b border-hairline">
      <div className="mx-auto max-w-[1400px] px-4 py-12 lg:px-6">
        <p className="font-mono text-xs text-body">{eyebrow}</p>
        <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight tracking-[-1.28px] text-ink">{title}</h1>
        {children ? <div className="mt-4 max-w-2xl text-base leading-7 text-body">{children}</div> : null}
      </div>
    </section>
  );
}
