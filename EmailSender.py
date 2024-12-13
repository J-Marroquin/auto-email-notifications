import smtplib
import configparser
from Logger import Logger
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

class EmailSender:
    def __init__(self, config_file='config.ini'):
        """
        Inicializa la clase EmailSender leyendo la configuración
        desde un archivo INI y configurando el logging.
        """
        # Leer configuración del archivo INI
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # Configuración del servidor SMTP
        self.SMTP_SERVER = self.config['SMTP']['SMTP_SERVER']
        self.SMTP_PORT = self.config['SMTP']['SMTP_PORT']
        self.EMAIL_ADDRESS = self.config['SMTP']['EMAIL_ADDRESS']
        self.EMAIL_PASSWORD = self.config['SMTP']['EMAIL_PASSWORD']
        self.recipients = self.config['PRODUCTION']['TO']

        # Configuración del directorio de logs
        self.logger = Logger()  

    def send_mail(self,subject:str,ratio:float, image_path:str):
        """
        Envía un correo electrónico con un gráfico y un mensaje HTML personalizado.
        
        param subject: Asunto del correo
        param ratio: Ratio de cambio que determinará si es "↑" o "↓"
        param image_path: Ruta al archivo de imagen (gráfico) adjunto
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.EMAIL_ADDRESS
            msg['To'] = self.recipients
            msg['Subject'] = subject
            flecha = "↑" if ratio > 0 else "↓"
            html =  f"""
            <html>
                <body>
                    <p>La variación de cobros para la compañia ayer fue de {ratio}% {flecha}.</p>
                    <p>
                        <img src="cid:graph_image" alt="Gráfica de Cobros" style="width:100%; height:auto;">
                    </p>
                </body>
            </html>
            """
            msg.attach(MIMEText(html,'html'))
            with open(image_path, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data, name= "graph_image")
                image.add_header('Content-ID', '<graph_image>')
                msg.attach(image)

            # Conexión al servidor SMTP
            server = smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT)
            server.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
            server.send_message(msg)

            self.logger.log_info(f"Correo enviado con éxito a {self.recipients} con asunto: {subject}")
            server.quit()
        except smtplib.SMTPException as e:
            self.logger.log_error(f"Error al conectar o enviar el correo: {e}")
        except FileNotFoundError:
            self.logger.log_error(f"Error: El archivo de imagen no se encontró en la ruta proporcionada: {image_path}")
        except Exception as e:
            self.logger.log_error(f"Error inesperado: {e}")


