import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class Logger:
    def __init__(self, log_dir='logs'):
        """
        Inicializa la configuración del sistema de logging.
        
        :param log_dir: Directorio donde se guardarán los logs. Por defecto es 'logs'.
        """
        self.log_dir = log_dir
        self.setup_logging()

    def setup_logging(self):
        """
        Configura el logging para guardar los logs en la carpeta `logs`.
        Los logs se almacenan en archivos rotativos diarios con el nombre `log_YYYY-MM-DD.txt`.
        """
        # Crear la carpeta 'logs' si no existe
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Obtener el nombre del archivo de log basado en la fecha actual
        log_filename = os.path.join(self.log_dir, 'log_' + self.get_current_date() + '.txt')

        # Configurar el handler para rotación diaria de logs
        log_handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=7, encoding= 'utf-8-sig')
        log_handler.suffix = "%Y-%m-%d.txt"  # Formato de la fecha en el nombre del archivo

        # Configuración del formato del log
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,  # Puedes usar DEBUG, INFO, WARNING, ERROR, CRITICAL
            format=log_format,
            handlers=[
                log_handler,  # Usamos el handler para rotación diaria
                logging.StreamHandler()  # También imprimimos en consola
            ]
        )

    def get_current_date(self):
        """
        Devuelve la fecha actual en formato YYYY-MM-DD.
        """
        return datetime.now().strftime("%Y-%m-%d")

    def log_info(self, message):
        """
        Registra un mensaje de nivel INFO.
        
        :param message: El mensaje que se desea registrar.
        """
        logging.info(message)

    def log_warning(self, message):
        """
        Registra un mensaje de nivel WARNING.
        
        :param message: El mensaje que se desea registrar.
        """
        logging.warning(message)

    def log_error(self, message):
        """
        Registra un mensaje de nivel ERROR.
        
        :param message: El mensaje que se desea registrar.
        """
        logging.error(message)

    def log_exception(self, exception):
        """
        Registra un mensaje de nivel ERROR con detalles de la excepción.
        
        :param exception: La excepción que se desea registrar.
        """
        logging.error("Excepción ocurrida", exc_info=exception)


# Uso de la clase Logger
if __name__ == "__main__":
    logger = Logger()

    # Registra algunos mensajes de ejemplo
    logger.log_info("Este es un mensaje de información.")
    logger.log_warning("Este es un mensaje de advertencia.")
    logger.log_error("Este es un mensaje de error.")
