import os
import sys
import psycopg2
import configparser
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import imaplib
from datetime import datetime as dt 
from datetime import timedelta as td
from typing import Tuple
import ReportGenerator
import EmailSender
import Logger

class Program:
    def __init__(self):
        """
        Inicializa el servicio de generación de reportes y logging.

        Calcula las fechas de inicio (un mes atrás) y fin (ayer) para generar el reporte.
        Configura el logger para registrar los eventos importantes del proceso.
        """
        if getattr(sys, 'frozen', False):
            # El programa está empaquetado
            self.BASE_DIR = os.path.dirname(sys.executable)
        else:
            # El programa se ejecuta como script
            self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.logger = Logger.Logger(log_dir= os.path.join(self.BASE_DIR, 'logs'))

        self.fin = (dt.now() - td(days=1)).strftime('%Y-%m-%d')
        self.inicio = (dt.now() - td(days=30)).strftime('%Y-%m-%d')

        self.logger.log_info(f"Reporte generado: Inicio = {self.inicio}, Fin = {self.fin}") 
        
    
    def main(self):
        """
        Orquesta la generación del reporte y el envío del correo.

        Llama a los métodos `generate_report` y `send_email` para generar el reporte 
        y enviarlo a los destinatarios. Registra los eventos de inicio, éxito y error
        en el proceso.

        Si ocurre un error en cualquier parte del proceso, se registra y el flujo 
        de trabajo se detiene.
        """
        try:
            self.logger.log_info("Iniciando proceso de generación y envío de reporte.")
            path, ratio, subject = self.generate_report()
            self.send_email(subject, ratio, path)
            self.logger.log_info("Proceso completado exitosamente.")
        
        except Exception as e:
            self.logger.log_error(f"Error en el proceso completo: {str(e)}")

    def generate_report(self)-> Tuple[str, float, str]:
        """
        Genera el reporte basado en el rango de fechas y calcula el ratio de variación.

        Este método crea una instancia de la clase `ReportGenerator` para generar un reporte 
        a partir de las fechas de inicio y fin calculadas. También calcula el ratio de cambio
        y devuelve el archivo generado, el ratio y el asunto del correo.

        Returns:
            path (str): Ruta del archivo generado.
            ratio (float): El ratio de variación calculado.
            subject (str): El asunto del correo con el ratio y la flecha (↑/↓).

        Raises:
            Exception: Si ocurre un error al generar el reporte.
        """
        try:
            oReportGenerator = ReportGenerator.ReportGenerator(reports_dir = os.path.join(self.BASE_DIR, 'reports'))  
            path, ratio = oReportGenerator.generate_report(self.inicio, self.fin)
            flecha = "↑" if ratio > 0 else "↓"
            subject = f'On Demand {ratio}% {flecha}'
            self.logger.log_info(f"Reporte generado: {path} con ratio {ratio}%")
            
            return path, ratio, subject

        except Exception as e:
            self.logger.log_error(f"Error al generar el reporte: {str(e)}")
            raise

    def send_email(self, subject:str, ratio:float, path:str) -> None:
        """
        Envía el correo con el reporte generado.

        Este método utiliza la clase `EmailSender` para enviar el correo con el archivo 
        de reporte adjunto, el asunto generado con el ratio y la flecha correspondiente.
        
        Parameters:
            to (str): Dirección de correo electrónico del destinatario.
            subject (str): Asunto del correo, incluye el ratio y la flecha (↑/↓).
            ratio (float): El ratio de variación de los cobros.
            path (str): Ruta del archivo del reporte que se va a adjuntar.

        Raises:
            Exception: Si ocurre un error al enviar el correo.
        """
        try:
            oEmailSender = EmailSender.EmailSender()  
            oEmailSender.send_mail(subject, ratio, path)
        
        except Exception as e:
            self.logger.log_error(f"Error al enviar el correo: {e}")


if __name__ == "__main__":
    service = Program()  
    service.main()  