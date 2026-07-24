"""Genera documentos PDF/CSV sintéticos de NeoBank Alura (fintech ficticia)."""

from __future__ import annotations

import csv
from pathlib import Path

from fpdf import FPDF

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


class NeoBankPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(20, 80, 120)
        self.cell(0, 8, "NeoBank Alura - Documento interno", align="L")
        self.ln(12)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title: str) -> None:
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(10, 40, 70)
        self.multi_cell(0, 8, title)
        self.ln(2)

    def body(self, text: str) -> None:
        self.set_font("Helvetica", "", 11)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, text)
        self.ln(3)


def _pdf() -> NeoBankPDF:
    pdf = NeoBankPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    return pdf


def generate_politicas_cuenta(path: Path) -> None:
    pdf = _pdf()
    pdf.section_title("1. Politicas de cuenta NeoBank Alura")
    pdf.body(
        "NeoBank Alura es un banco digital ficticio orientado a personas y "
        "pequenos negocios en Mexico y Latinoamerica. Este documento describe "
        "las politicas de apertura, verificacion KYC, limites operativos y "
        "bloqueo de cuentas."
    )
    pdf.section_title("1.1 Apertura de cuenta")
    pdf.body(
        "Para abrir una cuenta de ahorro digital el cliente debe: "
        "1) ser mayor de 18 anos; 2) contar con identificacion oficial vigente "
        "(INE/pasaporte); 3) proporcionar CURP y RFC cuando aplique; "
        "4) aceptar los terminos y condiciones en la app. "
        "La cuenta se activa en estado 'pendiente de verificacion' hasta "
        "completar el KYC."
    )
    pdf.section_title("1.2 Verificacion KYC")
    pdf.body(
        "El proceso KYC incluye captura de documento de identidad, selfie "
        "con prueba de vida y validacion de domicilio (comprobante no mayor "
        "a 3 meses). El nivel basico permite depositos hasta 20,000 MXN "
        "mensuales. El nivel completo eleva el limite a 150,000 MXN mensuales "
        "previa revision de riesgo."
    )
    pdf.section_title("1.3 Limites de transferencia")
    pdf.body(
        "Transferencias SPEI nacionales: hasta 50,000 MXN por operacion y "
        "100,000 MXN diarios en nivel completo. Transferencias entre cuentas "
        "NeoBank: sin comision y con limite diario de 200,000 MXN. "
        "Transferencias internacionales (SWIFT): requieren nivel completo y "
        "aprobacion adicional; limite de 10,000 USD por mes calendario."
    )
    pdf.section_title("1.4 Bloqueo y suspension")
    pdf.body(
        "La cuenta puede bloquearse temporalmente por: intentos fallidos de "
        "acceso (5 intentos), reporte de fraude, actividad inusual detectada "
        "por el motor de riesgo, o solicitud del titular. El desbloqueo "
        "requiere autenticacion reforzada (2FA) y, en casos de fraude, "
        "contacto con soporte en soporte@neobank-alura.example."
    )
    pdf.output(str(path))


def generate_tarifas_pdf(path: Path) -> None:
    pdf = _pdf()
    pdf.section_title("2. Tarifas y comisiones NeoBank Alura")
    pdf.body(
        "Las tarifas vigentes aplican a cuentas de personas fisicas. "
        "NeoBank Alura no cobra mensualidad por mantenimiento de cuenta "
        "de ahorro digital mientras exista al menos una operacion en los "
        "ultimos 12 meses."
    )
    pdf.section_title("2.1 Transferencias")
    pdf.body(
        "SPEI saliente: 8.00 MXN por operacion. SPEI entrante: sin costo. "
        "Transferencia entre cuentas NeoBank: 0.00 MXN. "
        "SWIFT internacional: 250.00 MXN + tipo de cambio del dia."
    )
    pdf.section_title("2.2 Retiros y tarjetas")
    pdf.body(
        "Retiro en cajeros de la red aliada: primeros 3 retiros del mes "
        "gratis; a partir del cuarto, 15.00 MXN. Retiro en cajero externo: "
        "30.00 MXN. Reposicion de tarjeta debit: 80.00 MXN. "
        "Compra en comercio nacional con tarjeta debit: sin comision."
    )
    pdf.section_title("2.3 Otros servicios")
    pdf.body(
        "Pago de servicios (agua, luz, telefono) via app: 5.00 MXN. "
        "Consulta de saldo en cajero: 5.00 MXN. Estado de cuenta digital "
        "mensual: gratis. Estado de cuenta impreso bajo demanda: 40.00 MXN."
    )
    pdf.output(str(path))


def generate_seguridad(path: Path) -> None:
    pdf = _pdf()
    pdf.section_title("3. Seguridad y prevencion de fraude")
    pdf.body(
        "La seguridad de la cuenta es responsabilidad compartida entre "
        "NeoBank Alura y el cliente. Este documento resume medidas tecnicas "
        "y recomendaciones de uso."
    )
    pdf.section_title("3.1 Autenticacion de dos factores (2FA)")
    pdf.body(
        "El 2FA es obligatorio para transferencias mayores a 5,000 MXN y "
        "para cambios de datos sensibles (correo, telefono, NIP). "
        "Para activar 2FA: abrir la app > Configuracion > Seguridad > "
        "Activar 2FA > escanear codigo QR con una app autenticadora "
        "(Google Authenticator, Authy u compatible) > confirmar con el "
        "codigo de 6 digitos. Tambien se puede usar SMS OTP como respaldo."
    )
    pdf.section_title("3.2 Phishing y correos falsos")
    pdf.body(
        "NeoBank Alura nunca solicita contrasenas, NIP ni codigos 2FA por "
        "correo, SMS o redes sociales. Los dominios oficiales terminan en "
        "neobank-alura.example. Ante un mensaje sospechoso: no hacer clic "
        "en enlaces, reportar a seguridad@neobank-alura.example y cambiar "
        "la contrasena desde la app oficial."
    )
    pdf.section_title("3.3 Robo o compromiso de credenciales")
    pdf.body(
        "Si el cliente sospecha robo de credenciales debe: 1) bloquear la "
        "cuenta desde la app (Boton de panico) o llamando a la linea 800-NEO-0000; "
        "2) restablecer contrasena; 3) rotar 2FA; 4) revisar movimientos de "
        "las ultimas 72 horas; 5) abrir ticket de disputa en menos de 48 horas "
        "para operaciones no reconocidas. NeoBank investiga y responde en "
        "hasta 10 dias habiles."
    )
    pdf.section_title("3.4 Dispositivos de confianza")
    pdf.body(
        "Solo se permiten hasta 3 dispositivos de confianza simultaneos. "
        "Un nuevo dispositivo requiere aprobacion por 2FA. Los dispositivos "
        "inactivos por 90 dias se eliminan automaticamente de la lista."
    )
    pdf.output(str(path))


def generate_terminos(path: Path) -> None:
    pdf = _pdf()
    pdf.section_title("4. Terminos y condiciones de uso")
    pdf.body(
        "Al usar la aplicacion NeoBank Alura el usuario acepta estos terminos. "
        "El servicio se ofrece 'tal cual' para fines educativos del Challenge "
        "Alura Agent; no constituye oferta bancaria real."
    )
    pdf.section_title("4.1 Uso de la aplicacion")
    pdf.body(
        "El usuario se compromete a proporcionar informacion veraz, no "
        "compartir credenciales y utilizar la cuenta solo para fines licitos. "
        "Esta prohibido el uso automatizado no autorizado (bots de scraping "
        "agresivo) y cualquier intento de vulnerar la seguridad de la "
        "plataforma."
    )
    pdf.section_title("4.2 Responsabilidad")
    pdf.body(
        "NeoBank Alura no responde por perdidas derivadas de negligencia del "
        "usuario (compartir NIP, instalar malware, ignorar alertas de "
        "seguridad). Las disputas por cargos no reconocidos siguen el "
        "proceso descrito en la politica de seguridad y fraude."
    )
    pdf.section_title("4.3 Privacidad de datos")
    pdf.body(
        "Los datos personales se tratan conforme a la Ley Federal de "
        "Proteccion de Datos Personales en Posesion de los Particulares "
        "(Mexico), de forma analoga. El usuario puede solicitar acceso, "
        "rectificacion, cancelacion u oposicion (ARCO) escribiendo a "
        "privacidad@neobank-alura.example. Los datos de sesion se conservan "
        "12 meses; los documentos KYC, 5 anos tras el cierre de cuenta."
    )
    pdf.section_title("4.4 Modificaciones")
    pdf.body(
        "NeoBank Alura puede actualizar tarifas y politicas con aviso de "
        "30 dias en la app y por correo. El uso continuado tras la fecha "
        "de vigencia implica aceptacion de los cambios."
    )
    pdf.output(str(path))


def generate_tarifas_csv(path: Path) -> None:
    rows = [
        {
            "codigo": "SPEI_OUT",
            "concepto": "Transferencia SPEI saliente",
            "moneda": "MXN",
            "comision": "8.00",
            "notas": "Por operacion",
        },
        {
            "codigo": "SPEI_IN",
            "concepto": "Transferencia SPEI entrante",
            "moneda": "MXN",
            "comision": "0.00",
            "notas": "Sin costo",
        },
        {
            "codigo": "NEO_P2P",
            "concepto": "Transferencia entre cuentas NeoBank",
            "moneda": "MXN",
            "comision": "0.00",
            "notas": "Sin comision",
        },
        {
            "codigo": "SWIFT",
            "concepto": "Transferencia internacional SWIFT",
            "moneda": "MXN",
            "comision": "250.00",
            "notas": "Mas tipo de cambio del dia",
        },
        {
            "codigo": "ATM_ALIADO",
            "concepto": "Retiro cajero red aliada (desde 4to)",
            "moneda": "MXN",
            "comision": "15.00",
            "notas": "Primeros 3 del mes gratis",
        },
        {
            "codigo": "ATM_EXT",
            "concepto": "Retiro cajero externo",
            "moneda": "MXN",
            "comision": "30.00",
            "notas": "Por operacion",
        },
        {
            "codigo": "CARD_REPLACE",
            "concepto": "Reposicion tarjeta debit",
            "moneda": "MXN",
            "comision": "80.00",
            "notas": "Por solicitud",
        },
        {
            "codigo": "BILL_PAY",
            "concepto": "Pago de servicios via app",
            "moneda": "MXN",
            "comision": "5.00",
            "notas": "Por pago",
        },
        {
            "codigo": "ATM_BALANCE",
            "concepto": "Consulta de saldo en cajero",
            "moneda": "MXN",
            "comision": "5.00",
            "notas": "Por consulta",
        },
        {
            "codigo": "STMT_PRINT",
            "concepto": "Estado de cuenta impreso",
            "moneda": "MXN",
            "comision": "40.00",
            "notas": "Bajo demanda",
        },
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["codigo", "concepto", "moneda", "comision", "notas"]
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    generate_politicas_cuenta(RAW_DIR / "politicas_cuenta.pdf")
    generate_tarifas_pdf(RAW_DIR / "tarifas_comisiones.pdf")
    generate_seguridad(RAW_DIR / "seguridad_fraude.pdf")
    generate_terminos(RAW_DIR / "terminos_condiciones.pdf")
    generate_tarifas_csv(RAW_DIR / "tarifas.csv")
    print(f"Documentos generados en: {RAW_DIR}")
    for p in sorted(RAW_DIR.iterdir()):
        if p.is_file():
            print(f"  - {p.name} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
