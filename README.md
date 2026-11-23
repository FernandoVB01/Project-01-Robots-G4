# Ackermann Challenger · Grupo 4

## Resumen

Robot móvil con dirección Ackermann, diseñado en Fusion 360 y simulado en Gazebo Harmonic con ROS 2 Jazzy. El controlador Pure Pursuit completó un circuito hexagonal redondeado de **14,69 m** con seis rectas y seis arcos circulares de 0,95 m de radio.

| Resultado de la corrida grabada | Valor |
|---|---:|
| Tiempo de simulación | 27,50 s |
| Error RMS de seguimiento | 2,0 mm |
| Error máximo de seguimiento | 5,6 mm |
| Distancia a la meta al ordenar la parada | 6,60 cm |

## Video de la simulación

[![Vista previa animada del Challenger recorriendo el circuito hexagonal en Gazebo. Abre el video completo.](Project-01-Robots-G4/docs/resultados/imagenes/gazebo-vista-previa.gif)](Project-01-Robots-G4/docs/resultados/gazebo_trayectoria.mp4)

La vista previa está acelerada. [Ver video completo en MP4](Project-01-Robots-G4/docs/resultados/gazebo_trayectoria.mp4)

## Evidencia de seguimiento

![Gráfica de la trayectoria de referencia y la trayectoria registrada del eje trasero en Gazebo](Project-01-Robots-G4/docs/resultados/imagenes/trajectory.png)

La gráfica superpone la referencia y el recorrido medido del eje trasero. [Ver captura de Gazebo, diseño CAD y gráfica de error](Project-01-Robots-G4/README.md#evidencias-de-la-simulación) · [Datos de la corrida](Project-01-Robots-G4/docs/resultados/tracking.csv)

## Ejecución y entregables

- [Dependencias, compilación y comandos de ROS 2](Project-01-Robots-G4/README.md#compilar-y-ejecutar)
- [Planos, informe IEEE y diapositivas](Project-01-Robots-G4/README.md#entregables)
