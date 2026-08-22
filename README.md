# Myssembler (Desactualizado)

### **¿Qué es MYSSEMBLER?**

MYSSEMBLER es un ensamblador personalizado diseñado para el computador básico del ramo **Arquitectura de Computadores (IIC2343)** de la Pontificia Universidad Católica de Chile. El hardware está programado en VHDL en la plataforma Vivado y diseñado para ser cargado en una tarjeta Basys 3 con arquitectura Artix-7. Este proyecto tiene un fin meramente investigativo, de práctica y estudio de la materia.

### **¿Qué hace MYSSEMBLER?**

Se encarga de traducir código en lenguaje ensamblador a los OPCODES compatibles con la arquitectura del computador básico. Soporta exclusivamente las especificaciones y estructuras orientadas al curso, incluyendo la interfaz gráfica de usuario en PySide6 con soporte de pestañas, resaltado de sintaxis, consola de registros/logs y selección de arquitecturas ISA e interfaces seriales.

### **Estructura y Características Principales**

* **Interfaz Gráfica (GUI):** Desarrollada con PySide6, incluye una consola de entrada de código con autoidentación y resaltador de sintaxis personalizado para las instrucciones, pestañas de navegación (`Assembler`, `Opcodes`, `ISA`), y una consola de logs integrada.
* **Selectores de ISA y Puertos:** Selector dinámico de arquitectura ISA y selector de puertos serie (COM/TTY) utilizando la librería `serial` para la conexión de hardware.
* **Importación de Archivos:** Permite importar archivos de código fuente directamente mediante un botón dedicado para cargarlos en la consola de edición.
* **Traducción de Opcodes:** Conversión de ensamblador a las secuencias de bits y códigos de operación definidos para el computador básico.

### **Traducción a Opcodes y Hardware**

#### Código Propietario:

* **Tabla de Bits:**

![alt text](image/tabla_de_bits.png)

* **Tabla de Operaciones:**

![alt text](image/tabla_de_operaciones.png)

* **Diagrama de Hardware (Assembly):**

![alt text](image/diagrama_computador_basico_assembly.png)

* **Programador computador basico:**

```vhdl
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity  Programmer is
    Port ( rx : in std_logic;
           tx : out std_logic;
           clk : in std_logic;
           clock : in std_logic;
           bussy   : out std_logic;
           ready   : out std_logic;
           address : out std_logic_vector (11 downto 0);
           dataout : out std_logic_vector (35 downto 0));
end Programmer;

architecture Behavioral of Programmer is

component UART 
    Port (  clk      : in  std_logic;
            rx       : in  std_logic;
            tx       : out  std_logic;
            reset    : in  std_logic;
            tx_enable: in  std_logic;
            rx_enable: out  std_logic;
            tx_ready : out  std_logic;
            rx_data  : out  std_logic_vector (7 downto 0);
            tx_data  : in std_logic_vector (7 downto 0)
            );
    end component;

signal tx_ready      : std_logic;
signal tx_enable     : std_logic;
signal rx_enable     : std_logic;
signal rx_data       : std_logic_vector (7 downto 0);
signal tx_data      : std_logic_vector (7 downto 0);

type memory_array is array (0 to 5) of std_logic_vector (7 downto 0);
signal memory : memory_array;

signal state : std_logic_vector(4 downto 0);
signal ready_sinc : std_logic;
signal bussy_sinc : std_logic;

 
begin

tx_data <= "00000000";
tx_enable <= '0';

bussy_prosses: process (clock, bussy_sinc)
        begin
          if bussy_sinc = '1' then
            bussy <= '1';
          elsif (rising_edge(clock)) then
            if (bussy_sinc = '0') then
              bussy <= '0';
            end if;
          end if;
        end process;


ready_prosses: process (clk)
        begin
          if (rising_edge(clk)) then
            if (ready_sinc = '1') then
              ready <= '1';
            else
              ready <= '0';
            end if;
          end if;
        end process;


data_prosses: process (rx_enable)
        begin
          if (rising_edge(rx_enable)) then
            if ( state = "00000" and rx_data = "11111111" ) then
                bussy_sinc <= '0';
                ready_sinc <= '0';
            elsif( state = "00000" and rx_data = "10101010") then 
                state <= "00001";
                ready_sinc <= '0';
            elsif( state = "00001" and rx_data = "10101010") then
                bussy_sinc <= '1';
                state <= "10001"; 
            elsif( state = "00001") then
                state <= "00000"; 
            elsif ( state = "10001" ) then
                memory(0) <= rx_data;
                state <= "10010";
            elsif ( state = "10010") then
                memory(1) <= rx_data;
                state <= "10011";
            elsif ( state = "10011" ) then
                memory(2) <= rx_data;
                state <= "10100";
            elsif ( state = "10100" ) then
                memory(3) <= rx_data;
                state <= "10101";  
            elsif ( state = "10101" ) then
                memory(4) <= rx_data;
                state <= "10110";   
            elsif ( state = "10110" ) then
                memory(5) <= rx_data;
                state <= "10111";  
            elsif ( state = "10111" and rx_data = "10101010" ) then
                state <= "00000";
                ready_sinc <= '1';
                address <= memory(0) & memory(1)(7 downto 4);
                dataout <= memory(1)(3 downto 0) & memory(2) & memory(3) & memory(4) & memory(5);   
            elsif ( state = "10111") then
                state <= "00000";
            end if;
          end if;
        end process;

inst_UART: UART port map(
        clk       => clk,
        rx        => rx,
        tx        => tx,
        reset     => '0',
        tx_enable => tx_enable,
        rx_enable => rx_enable,
        tx_ready  => tx_ready,
        rx_data   => rx_data,
        tx_data   => tx_data
    );   

end Behavioral;
```



### **Dependencias del Proyecto**

Para ejecutar y compilar MYSSEMBLER de manera local, se requieren los siguientes paquetes y librerías de Python:

* **PySide6** : Framework de interfaz gráfica de usuario.
* **pyserial** : Comunicación serial con puertos COM/TTY para programar la tarjeta física.
* **tabulate** : Generación de tablas formateadas en texto (utilizada para visualizar la consola de ISA).
* **PyInstaller** : Utilizado para la compilación y empaquetado del proyecto en un binario ejecutable independiente.

Además se añade el ejecutable MYSSEMBLER para linux y MYSSEMBLER.exe para windows
