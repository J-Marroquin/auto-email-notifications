import os
import sys
import psycopg2
import configparser
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from typing import Tuple
from Logger import Logger


class ReportGenerator:
    def __init__(self,config_file='config.ini', reports_dir = 'reports' ):
        """
        Inicializa la clase ReportGenerator leyendo la configuración 
        desde un archivo INI y configurando el logging.
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # Configuración de la base de datos
        self.DB_CONFIG = {
            'database': self.config['PRODUCTION']['DB_NAME'],
            'user': self.config['PRODUCTION']['DB_USER'],
            'password': self.config['PRODUCTION']['DB_PASSWORD'],
            'host': self.config['PRODUCTION']['DB_SERVER'],  # Cambia a la IP/host de tu servidor si no está local
            'port': self.config['PRODUCTION']['DB_PORT']  # Puerto predeterminado de PostgreSQL
        }
        
        self.output_dir = reports_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        # Configuración de logging
        self.logger = Logger()

    def generate_report(self,_dte_inicio:str, _dte_fin:str, _id_club = 166) -> Tuple[str, float]:
        """
        Genera un informe de cobros para un rango de fechas dado y un club específico.
        
            -param _dte_inicio ('%Y-%m-%d'): Fecha de inicio del reporte
            -param _dte_fin ('%Y-%m-%d'): Fecha de fin del reporte
            -param _id_club: ID del club (default 166)
            -return: Ruta al archivo de la imagen generada y el ratio calculado
        """
        try:
            # Establecer la conexión
            connection = psycopg2.connect(**self.DB_CONFIG)
            cursor = connection.cursor()

            query = "SELECT * FROM cobros_new.rpt_detallecobros(%s, %s, %s);"
            cursor.execute(query, (_id_club, _dte_inicio, _dte_fin))

            # Obtener el resultado y pasarlo a un DataFrame
            columns = [desc[0] for desc in cursor.description]  # Extraer nombres de columnas
            rows = cursor.fetchall()  # Obtener todos los registros
            df = pd.DataFrame(rows, columns=columns)
            self.logger.log_info("Consulta ejecutada exitosamente.")
        except Exception as e:
            self.logger.log_error(f"Error al ejecutar la consul;ta: {e}")
        finally:
            # Cerrar conexión
            if 'connection' in locals() and connection:
                cursor.close()
                connection.close()
                self.logger.log_info("Conexión cerrada.")

        df['dte_fecha'] = pd.to_datetime(df['dte_fecha'])
        df['n_fee'] = df['n_fee'].astype(float)
        df_431 = df[df["n_fee"] == 4.31].groupby("dte_fecha").sum()
        df_862 = df[df["n_fee"] == 8.62].groupby("dte_fecha").sum()
        grouped_total = df.groupby("dte_fecha").sum()
        
        try:
            ultimo_valor = grouped_total["i_total"].iloc[-1]
            penultimo_valor = grouped_total["i_total"].iloc[-2]
            ratio = ((ultimo_valor - penultimo_valor)/ penultimo_valor ) * 100
        except IndexError:
            self.logger.log_error("No se pudo calcular el ratio debido a un error de índices.")
            return None, None
        
        try:
            fig, ax1 = plt.subplots(figsize=(12, 6))
            width = 0.4

            # Gráfica de línea para `i_total`
            ax2 = ax1.twinx()
            ax2.fill_between(grouped_total.index, grouped_total["i_total"], color="#9ae9cf", alpha=0.5, label="n_monto (Total)")
            ax2.plot(grouped_total.index, grouped_total["i_total"], color="#04e397", linewidth=3, label="n_monto (Total)")
            ax2.tick_params(axis='y', labelcolor="green")
            ax2.set_yticks([])  
            ax2.set_ylabel(None)

            for spine in ax1.spines.values():
                spine.set_visible(False)  # Desactivar los bordes del eje principal
            for spine in ax2.spines.values():
                spine.set_visible(False)  # Desactivar los bordes del eje secundario

            ax1.spines["left"].set_visible(True)
            ax1.spines["left"].set_color("lightgrey")
            ax1.spines["left"].set_linewidth(0.7)  # Ajustar el grosor de la línea
            ax1.tick_params(bottom=False)

            ax1.bar(df_431.index - pd.Timedelta(days=0.2), df_431["i_total"], width=width, label="n_fee", color="#32adef", alpha=0.8,edgecolor="#199ef5",
                linewidth=2)
            ax1.bar(df_862.index + pd.Timedelta(days=0.2), df_862["i_total"], width=width, label="i_total", color="#D490D4", alpha=0.8, edgecolor="#a339b6", 
                linewidth=2)

            ax1.set_ylabel("Cobros", fontsize=12)
            ax1.set_xlabel("Fecha", fontsize=12)
            ax1.tick_params(axis='y')
            ax1.set_xticks(grouped_total.index)
            ax1.set_xticklabels(grouped_total.index.strftime('%Y-%m-%d'), rotation=45)

            ax1.grid(axis="y", linestyle="-", alpha=0.7)
            ax1.set_ylim(bottom=0)
            ax2.set_ylim(bottom=0)

            legend_elements = [
                Line2D([0], [0], color="#32adef", marker="o", markersize=8, label="Monto 5", linestyle="None"),
                Line2D([0], [0], color="#D490D4", marker="o", markersize=8, label="Monto 10", linestyle="None"),
                Line2D([0], [0], color="#04e397", marker="o", markersize=8, label="Total", linestyle="None"),
            ]

            plt.legend(
                handles= legend_elements,
                loc = "lower center",
                bbox_to_anchor=(0.5, -0.5),  # Ajustar posición debajo de la gráfica
                ncol=3,  # Número de columnas
                fontsize=10,  # Tamaño de fuente
                frameon=False  # Sin borde en la leyenda
            )

            # Mostrar la gráfica
            plt.tight_layout(rect=[0, 0, 1, 1])
            fig.legend(handles=legend_elements, loc="lower center", bbox_to_anchor=(0.5, -0.1), ncol=3, fontsize=10)
            output_path = os.path.join(self.output_dir, f"report_{_dte_inicio}_{_dte_fin}.png")
            plt.savefig(output_path)
            plt.close(fig)
            self.logger.log_info(f"Reporte generado exitosamente: {output_path}")
            return output_path, round(ratio,2)

        except Exception as e:
            self.logger.log_error(f"Error al generar la gráfica: {e}")
            return None, None

