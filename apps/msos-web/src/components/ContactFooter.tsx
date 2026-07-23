export function ContactFooter() {
  return (
    <footer
      aria-label="Contact"
      style={{
        margin: "0 clamp(24px, 4vw, 70px) 36px",
        paddingTop: 20,
        borderTop: "1px solid rgba(255, 255, 255, 0.08)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: 16,
        flexWrap: "wrap",
        color: "var(--muted)",
        fontSize: 13,
      }}
    >
      <span>Questions, partnerships, or feedback?</span>
      <a
        href="mailto:marketstructureos@gmail.com"
        style={{ color: "var(--teal)", fontWeight: 700 }}
      >
        marketstructureos@gmail.com
      </a>
    </footer>
  );
}
