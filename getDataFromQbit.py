# dependencies
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import datetime
import time
import mysql.connector
import logging
# logging.basicConfig(filename='/media/tenito/Syntegrar/Proyectos/syntedoQbit/', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

################################################################################
################################## INICIO BOT ##################################
################################################################################

# bloqueo de ventanas emergentes
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)

# ruta to driver de chrome descargado
driver = webdriver.Chrome("/usr/bin/chromedriver", chrome_options=chrome_options)


# link para abrir pagina web
driver.get("https://tickets.qbit.com.ar/otrs/index.pl?Action=AgentTicketSearch;Subaction=Search;TakeLastSearch=1;SaveProfile=1;Profile=Synte_Abiertos")
logging.info('########################## SE INICIA DESCARGA DE DATOS ##########################')

# target username y password
username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='User']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='Password']")))

# ingreso de credenciales en username and password
username.clear()
username.send_keys("") // Ingresar USERNAME
password.clear()
password.send_keys("") // Ingresar PASS

# btn de acceso con click event
button = (WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click())

# tiempo de espera tras login para carga de pantalla
time.sleep(2)

# btn de acceso con click event
# small = (WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "Small"))).click())

# scroll down
driver.execute_script("window.scrollTo(0, 4000);")
time.sleep(2)

# elementos de la tabla
rows = len(driver.find_elements_by_xpath("/html/body/div/div[4]/form/table/tbody/tr"))
cols = len(driver.find_elements_by_xpath("/html/body/div/div[4]/form/table/tbody/tr[1]/td"))

# Recorro las Rows para obtener la informacion y se guardan en los array
tickets = []
for r in range(1, rows + 1):
    for c in range(4, 5):  # for c in range(4, cols+1):
        value = driver.find_element_by_xpath("/html/body/div/div[4]/form/table/tbody/tr["+ str(r)+ "]/td["+ str(c)+ "]").text
    tickets.append(value)

asunto = []
for r in range(1, rows + 1):
    for c in range(5, 6):
        value = driver.find_element_by_xpath("/html/body/div/div[4]/form/table/tbody/tr["+ str(r)+"]/td["+ str(c)+ "]").text
    asunto.append(value)


# Validación caso que exista Página 2, sino existe solo guarda los datos de la Página 1
try:
    validatePage2 = driver.find_element(By.ID, "AgentTicketSearchPage2")

    page2 = (WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, "AgentTicketSearchPage2"))).click())

    # elementos de la tabla (pagina 2)
    rows = len(driver.find_elements_by_xpath("/html/body/div/div[4]/form/table/tbody/tr"))
    cols = len(driver.find_elements_by_xpath("/html/body/div/div[4]/form/table/tbody/tr[1]/td"))

    for r in range(1, rows + 1):
        for c in range(4, 5):  # for c in range(4, cols+1):
            value = driver.find_element_by_xpath("/html/body/div/div[4]/form/table/tbody/tr["+ str(r)+ "]/td["+ str(c)+ "]").text
        tickets.append(value)

    for r in range(1, rows + 1):
        for c in range(5, 6):
            value = driver.find_element_by_xpath("/html/body/div/div[4]/form/table/tbody/tr["+ str(r)+ "]/td["+ str(c)+ "]").text
        asunto.append(value)
    driver.quit()

except NoSuchElementException:
    driver.quit()

logging.info("########################## FINALIZA DESCARGA DE DATOS ##########################")

for i in range(0, len(tickets)): # string to number of tickets
    tickets[i] = int(tickets[i])

asunto = [s.replace('\n', ' ') for s in asunto]

########################################################################################
####################### INICIO PERSISTENCIA EN BASE DE DATOS SQL #######################
########################################################################################

dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

try:
    if len(tickets) == len(asunto):
        logging.info(f"Longitud de asunto: {len(asunto)}, longitud de tickets: {len(tickets)}")
        
        connection = mysql.connector.connect(host='', database='', user='', password='')
        
        logging.info("########################## CONEXION CON BASE DE DATOS ##########################")
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            querySelect = ("SELECT ID_Actividad FROM `actividades`")
            cursor.execute(querySelect)
            rows=cursor.fetchall()
            
            x = 0
            for ticket in tickets:
                existe = False
                for row in rows:
                    if ticket == row[0]:
                        existe = True
                if existe == False:
                    sqlInsert = (f"INSERT INTO `actividades` (Ticket, ID_Actividad_Padre, ID_Tipo_Actividad, ID_Estado, ID_Cliente, ID_Consultora, Nombre, Descripcion, Avance, Detalle, Horas, Detalle_Imputacion, Fecha_Liberacion, Funcional, Funcional_Visible, Aud_Fecha_Creacion, Aud_Creador, Aud_Fecha_Modif, Aud_Modificador) VALUES ('{tickets[x]}', 0, 16, 4, 58, 3, 'Ticket #{tickets[x]} - {asunto[x]}', '<p><br></p>', 0, '', 0, '', '0000-00-00', '', 0, '{dt}', 'Diego', '{dt}', 'Diego')")

                    # INSERT INTO `actividades` (`ID_Actividad`, `Ticket`, `ID_Actividad_Padre`, `ID_Tipo_Actividad`, `ID_Estado`, `ID_Cliente`, `ID_Consultora`, `ID_Tarjeta_Trello`, `Nombre`, `Descripcion`, `Avance`, `Detalle`, `Horas`, `Detalle_Imputacion`, `Fecha_Liberacion`, `Facturacion`, `Estimado_Facturacion`, `Funcional`, `Funcional_Visible`, `Fecha_Comienzo`, `Aud_Fecha_Creacion`, `Aud_Creador`, `Aud_Fecha_Modif`, `Aud_Modificador`) VALUES (NULL, '9999999', '0', '16', '4', '58', '3', NULL, 'local', '<p><br></p>', '0', NULL, NULL, NULL, '0000-00-00', NULL, NULL, NULL, '0', NULL, '2021-09-10 20:10:32.000000', NULL, '2021-09-10 20:10:32.000000', NULL);


                    cursor.execute(sqlInsert)
                    logging.info(f"Datos ingresados correctamente a la base de datos. Ticket N: {ticket} con asunto: {asunto[x]}")
                else:
                    logging.warning(f"Dato a ingresar ya existente - Ticket N: {ticket} -. No se ha ingresado a la base de datos")
                x = x+1
            connection.commit()
    else:
        logging.error("Longitud diferente entre tickets y asunto")

except (mysql.connector.IntegrityError, mysql.connector.DataError) as err:
    logging.error("DataError or IntegrityError")
    logging.error(err)
    connection.rollback()

except mysql.connector.ProgrammingError as err:
    logging.error("Programming Error")
    logging.error(err)
    connection.rollback()

except mysql.connector.Error as err:
    logging.error(err)
    connection.rollback()

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        logging.info("########################## CONEXION CON BASE DE DATOS CERRADA ##########################")
