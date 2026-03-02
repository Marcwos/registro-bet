"""
Plantillas HTML para emails transaccionales de RegistroBet.
Cada funcion retorna una tupla (subject, plain_text, html).
"""


def _base_template(title: str, body_html: str) -> str:
    """Envuelve el contenido en la plantilla base de RegistroBet."""
    return f"""\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0; padding:0; background-color:#f1f5f9; font-family:'Segoe UI',Roboto,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f1f5f9; padding:40px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="480" cellpadding="0" cellspacing="0"
               style="background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.08);">
          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#3b82f6,#2563eb); padding:28px 32px; text-align:center;">
              <span style="font-size:22px; font-weight:700; color:#ffffff; letter-spacing:-0.3px;">
                &#x1F4C8; RegistroBet
              </span>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:32px 32px 24px;">
              {body_html}
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:16px 32px 28px; border-top:1px solid #e2e8f0; text-align:center;">
              <p style="margin:0; font-size:12px; color:#94a3b8;">
                Este correo fue enviado automaticamente por RegistroBet.<br>
                Si no solicitaste esto, puedes ignorar este mensaje.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _code_block(code: str) -> str:
    """Renderiza el codigo de 6 digitos con estilo destacado."""
    spaced = "&nbsp;&nbsp;".join(code)
    return f"""\
<div style="text-align:center; margin:24px 0;">
  <span style="display:inline-block; background-color:#f1f5f9; border:2px dashed #3b82f6;
               border-radius:10px; padding:16px 32px; font-size:32px; font-weight:700;
               letter-spacing:8px; color:#1e293b; font-family:'Courier New',monospace;">
    {spaced}
  </span>
</div>"""


def build_verification_email(code: str) -> tuple[str, str, str]:
    """Construye el email de verificacion de cuenta.

    Returns:
        (subject, plain_text, html)
    """
    subject = "Verifica tu email - RegistroBet"

    plain = (
        f"¡Hola! Bienvenido a RegistroBet.\n\n"
        f"Tu codigo de verificacion es: {code}\n\n"
        f"Este codigo expira en 10 minutos.\n"
        f"Si tu no solicitaste esto, puedes ignorar este mensaje."
    )

    body_html = f"""\
<h2 style="margin:0 0 8px; font-size:20px; color:#1e293b;">&#161;Bienvenido a RegistroBet!</h2>
<p style="margin:0 0 20px; font-size:15px; color:#475569; line-height:1.6;">
  Para completar tu registro, usa el siguiente codigo de verificacion:
</p>
{_code_block(code)}
<p style="margin:0; font-size:13px; color:#64748b; text-align:center;">
  Este codigo expira en <strong>10 minutos</strong>.
</p>"""

    html = _base_template(subject, body_html)
    return subject, plain, html


def build_recovery_email(code: str) -> tuple[str, str, str]:
    """Construye el email de recuperacion de contrasena.

    Returns:
        (subject, plain_text, html)
    """
    subject = "Recupera tu contrasena - RegistroBet"

    plain = (
        f"Hola, recibimos una solicitud para restablecer tu contrasena.\n\n"
        f"Tu codigo de recuperacion es: {code}\n\n"
        f"Este codigo expira en 10 minutos.\n"
        f"Si tu no solicitaste esto, puedes ignorar este mensaje."
    )

    body_html = f"""\
<h2 style="margin:0 0 8px; font-size:20px; color:#1e293b;">Recupera tu contrasena</h2>
<p style="margin:0 0 20px; font-size:15px; color:#475569; line-height:1.6;">
  Recibimos una solicitud para restablecer tu contrasena. Usa el siguiente codigo:
</p>
{_code_block(code)}
<p style="margin:0; font-size:13px; color:#64748b; text-align:center;">
  Este codigo expira en <strong>10 minutos</strong>.
</p>"""

    html = _base_template(subject, body_html)
    return subject, plain, html
