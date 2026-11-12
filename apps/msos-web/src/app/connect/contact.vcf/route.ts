// This endpoint uses the same runtime phone configuration as the landing page.
// Never commit the owner's phone number to this public repository.
export const dynamic = "force-dynamic";

export function GET() {
  const phone = (process.env.MSOS_CONNECT_WHATSAPP_NUMBER ?? "").replace(/\D/g, "");
  const includePhone = /^\d{10,15}$/.test(phone);
  const lines = [
    "BEGIN:VCARD",
    "VERSION:3.0",
    "N:Tabakman;Daniel;;;",
    "FN:Daniel Tabakman",
    "TITLE:Product, Strategy & Systems",
    ...(includePhone ? [`TEL;TYPE=CELL:+${phone}`] : []),
    "URL:https://marketstructureos.com/connect",
    "URL;TYPE=WORK:https://marketstructureos.com/",
    "NOTE:LinkedIn https://ca.linkedin.com/in/daniel-tabakman-5361b6196",
    "END:VCARD",
  ];

  return new Response(lines.join("\r\n") + "\r\n", {
    headers: {
      "Content-Type": "text/vcard; charset=utf-8",
      "Content-Disposition": 'attachment; filename="Daniel-Tabakman.vcf"',
      "Cache-Control": "no-store",
    },
  });
}
