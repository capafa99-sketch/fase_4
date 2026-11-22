
# ==========================================================
# PROYECTO: SOFTWARE FJ
# SISTEMA INTEGRAL DE GESTION DE CLIENTES, SERVICIOS Y RESERVAS
# Curso: Programacion - UNAD
# Fase 4 - Practicas simuladas
# ==========================================================

import logging
from abc import ABC, abstractmethod


# ==========================================================
# 1. CONFIGURACION DEL ARCHIVO DE LOGS
# ==========================================================

logging.basicConfig(
    filename="sistema.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# ==========================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ==========================================================

class ErrorSistema(Exception):
    """Excepcion general del sistema."""
    pass


class DatoInvalidoError(ErrorSistema):
    """Se presenta cuando un dato no es valido."""
    pass


class ReservaError(ErrorSistema):
    """Se presenta cuando ocurre un error en una reserva."""
    pass


class ServicioNoDisponibleError(ErrorSistema):
    """Se presenta cuando un servicio no esta disponible."""
    pass


# ==========================================================
# 3. CLASE ABSTRACTA ENTIDAD
# ==========================================================

class Entidad(ABC):

    def __init__(self, identificacion):
        if not isinstance(identificacion, str) or not identificacion.strip():
            raise DatoInvalidoError("La identificacion es obligatoria.")

        self._identificacion = identificacion.strip()

    @abstractmethod
    def mostrar_informacion(self):
        pass

# ==========================================================
# 4. CLASE CLIENTE
# ==========================================================

class Cliente(Entidad):

    def __init__(self, identificacion, nombre, correo, telefono):
        super().__init__(identificacion)

        if not isinstance(nombre, str) or not nombre.strip():
            raise DatoInvalidoError("El nombre no puede estar vacio.")

        if not isinstance(correo, str) or "@" not in correo or "." not in correo:
            raise DatoInvalidoError("El correo electronico no es valido.")

        if not isinstance(telefono, str) or not telefono.isdigit() or len(telefono) < 7:
            raise DatoInvalidoError("El telefono debe tener minimo 7 digitos.")

        self.__nombre = nombre.strip()
        self.__correo = correo.strip()
        self.__telefono = telefono.strip()

        logging.info("Cliente registrado: %s", self.__nombre)

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    def mostrar_informacion(self):
        return (
            f"Identificacion: {self.identificacion}\n"
            f"Nombre: {self.__nombre}\n"
            f"Correo: {self.__correo}\n"
            f"Telefono: {self.__telefono}"
        )


# ==========================================================
# 5. CLASE ABSTRACTA SERVICIO
# ==========================================================

class Servicio(Entidad):

    def __init__(self, identificacion, nombre, tarifa):
        super().__init__(identificacion)

        if not isinstance(nombre, str) or not nombre.strip():
            raise DatoInvalidoError("El nombre del servicio es obligatorio.")

        if isinstance(tarifa, bool) or not isinstance(tarifa, (int, float)) or tarifa <= 0:
            raise DatoInvalidoError("La tarifa debe ser un numero mayor que cero.")

        self.nombre = nombre.strip()
        self.tarifa = float(tarifa)
        self.disponible = True

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def descripcion(self):
        pass

    @staticmethod
    def _validar_duracion(duracion, mensaje):
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatoInvalidoError(mensaje)

    def calcular_costo(self, duracion, impuesto=0, descuento=0):

        self.validar_parametros(duracion)

        if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)):
            raise DatoInvalidoError("El impuesto debe ser numerico.")

        if isinstance(descuento, bool) or not isinstance(descuento, (int, float)):
            raise DatoInvalidoError("El descuento debe ser numerico.")

        if not 0 <= impuesto <= 100:
            raise DatoInvalidoError("El impuesto debe estar entre 0 y 100.")

        if not 0 <= descuento <= 100:
            raise DatoInvalidoError("El descuento debe estar entre 0 y 100.")

        subtotal = self.tarifa * duracion
        valor_impuesto = subtotal * impuesto / 100
        valor_descuento = subtotal * descuento / 100

        total = subtotal + valor_impuesto - valor_descuento

        if total < 0:
            raise DatoInvalidoError("El calculo del costo es inconsistente.")

        return round(total, 2)

    def mostrar_informacion(self):
        return (
            f"Codigo: {self.identificacion}\n"
            f"Servicio: {self.nombre}\n"
            f"Descripcion: {self.descripcion()}\n"
            f"Tarifa por hora: ${self.tarifa:,.2f}\n"
            f"Disponible: {'Si' if self.disponible else 'No'}"
        )


# ==========================================================
# 6. SERVICIO ESPECIALIZADO: RESERVA DE SALAS
# ==========================================================

class ReservaSala(Servicio):

    def validar_parametros(self, duracion):
        self._validar_duracion(duracion, "La duracion de la sala debe ser mayor que cero.")

    def descripcion(self):
        return "Reserva de salas para reuniones y eventos."


# ==========================================================
# 7. SERVICIO ESPECIALIZADO: ALQUILER DE EQUIPOS
# ==========================================================

class AlquilerEquipo(Servicio):

    def validar_parametros(self, duracion):
        self._validar_duracion(duracion, "El tiempo de alquiler debe ser mayor que cero.")

    def descripcion(self):
        return "Alquiler de computadores y equipos tecnologicos."


# ==========================================================
# 8. SERVICIO ESPECIALIZADO: ASESORIAS
# ==========================================================

class Asesoria(Servicio):

    def validar_parametros(self, duracion):
        self._validar_duracion(duracion, "La duracion de la asesoria debe ser mayor que cero.")

    def descripcion(self):
        return "Asesorias y consultorias tecnologicas especializadas."


# ==========================================================
# 9. CLASE RESERVA
# ==========================================================

class Reserva(Entidad):

    def __init__(self, identificacion, cliente, servicio, duracion):
        super().__init__(identificacion)

        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("Debe seleccionar un cliente valido.")

        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("Debe seleccionar un servicio valido.")

        servicio.validar_parametros(duracion)

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.costo = 0

        logging.info("Reserva %s creada.", identificacion)


    def confirmar(self, impuesto=0, descuento=0):
        if self.estado != "Pendiente":
            raise ReservaError("Solamente se pueden confirmar reservas pendientes.")
        
        if not self.servicio.disponible:
            raise ServicioNoDisponibleError("El servicio no se encuentra disponible.")

        try:
            self.costo = self.servicio.calcular_costo(
                self.duracion, impuesto, descuento
            )
        except DatoInvalidoError as error:
            raise ReservaError(
                "No se pudo calcular el costo de la reserva."
            ) from error

        self.estado = "Confirmada"
        logging.info("Reserva %s confirmada.", self.identificacion)
        return self.costo

   
    def cancelar(self):

        if self.estado == "Cancelada":
            raise ReservaError("La reserva ya se encuentra cancelada.")

        self.estado = "Cancelada"

        logging.info("Reserva %s cancelada.", self.identificacion)

    def procesar(self):

        if self.estado != "Confirmada":
            raise ReservaError("La reserva debe estar confirmada para procesarse.")

        self.estado = "Procesada"

        logging.info("Reserva %s procesada.", self.identificacion)

    def mostrar_informacion(self):

        return (
            f"Reserva: {self.identificacion}\n"
            f"Cliente: {self.cliente.nombre}\n"
            f"Servicio: {self.servicio.nombre}\n"
            f"Duracion: {self.duracion} horas\n"
            f"Estado: {self.estado}\n"
            f"Costo: ${self.costo:,.2f}"
        )


# ==========================================================
# 10. CLASE GESTOR DEL SISTEMA
# ==========================================================

class GestorSistema:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):

        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("El objeto no es un cliente valido.")

        if any(c.identificacion == cliente.identificacion for c in self.clientes):
            raise DatoInvalidoError("El cliente ya se encuentra registrado.")

        self.clientes.append(cliente)
        logging.info("Cliente agregado al sistema.")

    def registrar_servicio(self, servicio):

        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El objeto no es un servicio valido.")

        if any(s.identificacion == servicio.identificacion for s in self.servicios):
            raise DatoInvalidoError("El servicio ya se encuentra registrado.")

        self.servicios.append(servicio)
        logging.info("Servicio agregado: %s", servicio.nombre)

    def registrar_reserva(self, reserva):

        if not isinstance(reserva, Reserva):
            raise DatoInvalidoError("La reserva no es valida.")

        if any(r.identificacion == reserva.identificacion for r in self.reservas):
            raise DatoInvalidoError("El codigo de reserva ya existe.")

        if reserva.cliente not in self.clientes:
            raise DatoInvalidoError("El cliente no esta registrado en el sistema.")

        if reserva.servicio not in self.servicios:
            raise DatoInvalidoError("El servicio no esta registrado en el sistema.")

        self.reservas.append(reserva)
        logging.info("Reserva agregada al sistema.")

    def mostrar_clientes(self):
        for cliente in self.clientes:
            print(cliente.mostrar_informacion())
            print("-" * 40)

    def mostrar_servicios(self):
        for servicio in self.servicios:
            print(servicio.mostrar_informacion())
            print("-" * 40)

    def mostrar_reservas(self):
        for reserva in self.reservas:
            print(reserva.mostrar_informacion())
            print("-" * 40)


# ==========================================================
# 11. FUNCION PARA CONTROLAR ERRORES
# ==========================================================

def ejecutar_operacion(descripcion, operacion):

    print(f"\n{descripcion}")

    try:
        operacion()

    except ErrorSistema as error:
        print("ERROR CONTROLADO:", error)
        logging.error("%s: %s", descripcion, error)

    except Exception as error:
        print("ERROR INESPERADO:", error)
        logging.exception("%s: error inesperado", descripcion)

    else:
        print("Operacion realizada correctamente.")

    finally:
        print("Finalizacion de la operacion.")


# ==========================================================
# 12. PRUEBAS AUTOMATICAS: 12 OPERACIONES
# ==========================================================

def ejecutar_pruebas():

    sistema = GestorSistema()

    print("\n" + "=" * 60)
    print("     PRUEBAS DEL SISTEMA INTEGRAL SOFTWARE FJ")
    print("=" * 60)

    # OPERACION 1: Registro de cliente valido

    def prueba_1():
        global cliente1
        cliente1 = Cliente(
            "1001", "Carlos Perez",
            "carlos@gmail.com", "3001234567"
        )
        sistema.registrar_cliente(cliente1)
        print(cliente1.mostrar_informacion())

    ejecutar_operacion("OPERACION 1: Registrar cliente valido", prueba_1)

    # OPERACION 2: Registro de cliente invalido

    def prueba_2():
        cliente = Cliente(
            "1002", "Maria Lopez",
            "correoIncorrecto", "3101234567"
        )
        sistema.registrar_cliente(cliente)

    ejecutar_operacion("OPERACION 2: Registrar cliente con correo invalido", prueba_2)

    # OPERACION 3: Registrar segundo cliente valido

    def prueba_3():
        global cliente2
        cliente2 = Cliente(
            "1003", "Ana Rodriguez",
            "ana@gmail.com", "3114567890"
        )
        sistema.registrar_cliente(cliente2)
        print(cliente2.mostrar_informacion())

    ejecutar_operacion("OPERACION 3: Registrar segundo cliente", prueba_3)

    # OPERACION 4: Crear servicio de salas

    def prueba_4():
        global sala
        sala = ReservaSala("S01", "Sala de reuniones", 50000)
        sistema.registrar_servicio(sala)
        print(sala.mostrar_informacion())

    ejecutar_operacion("OPERACION 4: Crear servicio de salas", prueba_4)

    # OPERACION 5: Crear servicio de equipos

    def prueba_5():
        global equipo
        equipo = AlquilerEquipo("S02", "Computador portatil", 30000)
        sistema.registrar_servicio(equipo)
        print(equipo.mostrar_informacion())

    ejecutar_operacion("OPERACION 5: Crear servicio de equipos", prueba_5)

    # OPERACION 6: Crear servicio de asesoria

    def prueba_6():
        global asesoria
        asesoria = Asesoria("S03", "Asesoria informatica", 80000)
        sistema.registrar_servicio(asesoria)
        print(asesoria.mostrar_informacion())

    ejecutar_operacion("OPERACION 6: Crear servicio de asesoria", prueba_6)

    # OPERACION 7: Crear servicio con tarifa invalida

    def prueba_7():
        servicio = ReservaSala("S04", "Sala invalida", -5000)
        sistema.registrar_servicio(servicio)

    ejecutar_operacion("OPERACION 7: Crear servicio con tarifa incorrecta", prueba_7)

    # OPERACION 8: Crear y registrar una reserva

    def prueba_8():
        global reserva1
        reserva1 = Reserva("R01", cliente1, sala, 2)
        sistema.registrar_reserva(reserva1)
        print(reserva1.mostrar_informacion())

    ejecutar_operacion("OPERACION 8: Crear reserva correctamente", prueba_8)

    # OPERACION 9: Confirmar reserva con impuesto y descuento

    def prueba_9():
        costo = reserva1.confirmar(impuesto=19, descuento=10)
        print(f"Costo total de la reserva: ${costo:,.2f}")
        print(reserva1.mostrar_informacion())

    ejecutar_operacion("OPERACION 9: Confirmar reserva", prueba_9)

    # OPERACION 10: Procesar reserva

    def prueba_10():
        reserva1.procesar()
        print(reserva1.mostrar_informacion())

    ejecutar_operacion("OPERACION 10: Procesar reserva", prueba_10)

    # OPERACION 11: Intentar reservar con duracion incorrecta

    def prueba_11():
        reserva = Reserva("R02", cliente2, equipo, 0)
        sistema.registrar_reserva(reserva)

    ejecutar_operacion("OPERACION 11: Crear reserva con duracion incorrecta", prueba_11)

    # OPERACION 12: Intentar confirmar servicio no disponible

    def prueba_12():
        servicio = Asesoria("S05", "Asesoria avanzada", 90000)
        sistema.registrar_servicio(servicio)

        reserva = Reserva("R03", cliente2, servicio, 1)
        sistema.registrar_reserva(reserva)

        servicio.disponible = False
        reserva.confirmar()

    ejecutar_operacion("OPERACION 12: Intentar reservar servicio no disponible", prueba_12)

    # OPERACION ADICIONAL: Cancelar reserva

    def prueba_13():
        reserva = Reserva("R04", cliente2, equipo, 2)
        sistema.registrar_reserva(reserva)
        reserva.cancelar()
        print(reserva.mostrar_informacion())

    ejecutar_operacion("OPERACION 13: Cancelar una reserva", prueba_13)

    print("\n" + "=" * 60)
    print("RESUMEN DEL SISTEMA")
    print("=" * 60)

    print("Clientes registrados:", len(sistema.clientes))
    print("Servicios registrados:", len(sistema.servicios))
    print("Reservas registradas:", len(sistema.reservas))

    print("\nCLIENTES:")
    sistema.mostrar_clientes()

    print("\nSERVICIOS:")
    sistema.mostrar_servicios()

    print("\nRESERVAS:")
    sistema.mostrar_reservas()

    print("\nLas pruebas finalizaron.")
    print("Los eventos y errores fueron registrados en sistema.log.")


# ==========================================================
# 13. MENU INTERACTIVO
# ==========================================================

def menu_principal():

    sistema = GestorSistema()

    while True:

        print("\n" + "=" * 50)
        print("        SISTEMA DE GESTION SOFTWARE FJ")
        print("=" * 50)
        print("1. Registrar cliente")
        print("2. Registrar servicio")
        print("3. Mostrar clientes")
        print("4. Mostrar servicios")
        print("5. Crear reserva")
        print("6. Confirmar reserva")
        print("7. Cancelar reserva")
        print("8. Mostrar reservas")
        print("9. Ejecutar pruebas automaticas")
        print("0. Salir")
        print("=" * 50)

        try:
            opcion = input("Seleccione una opcion: ").strip()

            if opcion == "1":

                cliente = Cliente(
                    input("Identificacion: ").strip(),
                    input("Nombre: ").strip(),
                    input("Correo: ").strip(),
                    input("Telefono: ").strip()
                )

                sistema.registrar_cliente(cliente)
                print("Cliente registrado correctamente.")

            elif opcion == "2":

                print("1. Reserva de salas")
                print("2. Alquiler de equipos")
                print("3. Asesorias")

                tipo = input("Seleccione el tipo de servicio: ").strip()

                codigo = input("Codigo del servicio: ").strip()
                nombre = input("Nombre del servicio: ").strip()
                tarifa = float(input("Tarifa por hora: "))

                if tipo == "1":
                    servicio = ReservaSala(codigo, nombre, tarifa)
                elif tipo == "2":
                    servicio = AlquilerEquipo(codigo, nombre, tarifa)
                elif tipo == "3":
                    servicio = Asesoria(codigo, nombre, tarifa)
                else:
                    raise DatoInvalidoError("Tipo de servicio incorrecto.")

                sistema.registrar_servicio(servicio)
                print("Servicio registrado correctamente.")

            elif opcion == "3":
                sistema.mostrar_clientes()

            elif opcion == "4":
                sistema.mostrar_servicios()

            elif opcion == "5":

                codigo = input("Codigo de reserva: ").strip()
                identificacion = input("Identificacion del cliente: ").strip()
                codigo_servicio = input("Codigo del servicio: ").strip()
                duracion = float(input("Duracion en horas: "))

                cliente = next(
                    (c for c in sistema.clientes
                     if c.identificacion == identificacion), None
                )

                servicio = next(
                    (s for s in sistema.servicios
                     if s.identificacion == codigo_servicio), None
                )

                if cliente is None:
                    raise DatoInvalidoError("Cliente no encontrado.")

                if servicio is None:
                    raise DatoInvalidoError("Servicio no encontrado.")

                reserva = Reserva(codigo, cliente, servicio, duracion)
                sistema.registrar_reserva(reserva)

                print("Reserva creada correctamente.")

            elif opcion == "6":

                codigo = input("Codigo de reserva: ").strip()

                reserva = next(
                    (r for r in sistema.reservas
                     if r.identificacion == codigo), None
                )

                if reserva is None:
                    raise ReservaError("Reserva no encontrada.")

                impuesto = float(input("Porcentaje de impuesto (0 si no aplica): "))
                descuento = float(input("Porcentaje de descuento (0 si no aplica): "))

                costo = reserva.confirmar(impuesto, descuento)

                print("Reserva confirmada.")
                print(f"Costo total: ${costo:,.2f}")

            elif opcion == "7":

                codigo = input("Codigo de reserva: ").strip()

                reserva = next(
                    (r for r in sistema.reservas
                     if r.identificacion == codigo), None
                )

                if reserva is None:
                    raise ReservaError("Reserva no encontrada.")

                reserva.cancelar()
                print("Reserva cancelada.")

            elif opcion == "8":
                sistema.mostrar_reservas()

            elif opcion == "9":
                ejecutar_pruebas()

            elif opcion == "0":
                print("Gracias por utilizar Software FJ.")
                logging.info("El usuario cerro el programa.")
                break

            else:
                raise DatoInvalidoError("Opcion no valida.")

        except ErrorSistema as error:
            print("ERROR CONTROLADO:", error)
            logging.error("Error en el menu: %s", error)

        except ValueError as error:
            print("ERROR: Debe ingresar un valor numerico valido.")
            logging.exception("Error de conversion de datos: %s", error)

        except Exception as error:
            print("ERROR INESPERADO:", error)
            logging.exception("Error inesperado en el menu.")

        finally:
            print("\nOperacion del menu finalizada.")


# ==========================================================
# 14. INICIO DEL PROGRAMA
# ==========================================================

if __name__ == "__main__":

    print("\nBIENVENIDO AL SISTEMA SOFTWARE FJ")

    while True:
        print("\nSeleccione el modo de ejecucion:")
        print("1. Ejecutar las 13 pruebas automaticas")
        print("2. Ingresar al menu interactivo")

        try:
            modo = input("Seleccione una opcion: ").strip()

            if modo == "1":
                ejecutar_pruebas()
                break

            elif modo == "2":
                menu_principal()
                break

            else:
                print("Seleccione 1 o 2.")

        except KeyboardInterrupt:
            print("\nPrograma interrumpido por el usuario.")
            logging.warning("Programa interrumpido.")
            break

        finally:
            print("Fin de la seleccion.")
