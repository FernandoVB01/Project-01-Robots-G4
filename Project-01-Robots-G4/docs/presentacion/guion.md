# Guion para el video del Grupo 4

**Duración objetivo: 4:45.** Graben en horizontal con diapositivas compartidas y cámara de los expositores. La diapositiva 1 sirve para presentar a todos en cámara. Si hay más de cuatro integrantes, dividan dos bloques entre los participantes adicionales. Si hay menos, una misma persona puede asumir dos bloques.

| Tiempo | Diapositivas | Intervención |
|---|---|---|
| 0:00–0:25 | 1 | Todo el equipo en cámara. Integrante A abre y presenta el proyecto. |
| 0:25–1:38 | 2–3 | Integrante A compara las cinemáticas y muestra la geometría del CAD. |
| 1:38–2:55 | 4–5 | Integrante B explica el modelo y el controlador. |
| 2:55–3:39 | 6 | Integrante C describe la corrida y sus métricas. |
| 3:39–4:45 | 7–8 y clip | Integrante D presenta la aplicación y cierra. |

## 1 · Apertura · 25 s

«Somos el Grupo 4. Nuestro robot, Ackermann Challenger, tiene dirección en las ruedas delanteras y tracción trasera. Nuestro objetivo fue llevar el diseño de Fusion 360 a Gazebo y cerrar el lazo en ROS 2 Jazzy. Elegimos una trayectoria en ocho porque exige cambiar de sentido de giro y pasar varias veces por el mismo cruce.»

## 2 · Comparación · 38 s

«El diferencial puede girar en el sitio con dos ruedas motrices. Un skid-steer también puede pivotar, pero sus ruedas fijas necesitan deslizar lateralmente durante el giro. Omni y Mecanum añaden desplazamiento lateral a cambio de depender de los rodillos. Un triciclo simplifica la dirección a una articulación y tiene un polígono de apoyo menor. Para curvas continuas sobre pavimento usamos Ackermann, que orienta las ruedas delanteras con ángulos diferentes y requiere un radio mínimo.»

## 3 · Diseño · 35 s

«El ensamble incluye la base, carrocería, dos manguetas, cuatro ruedas y el cuerpo del LiDAR. La distancia entre ejes es 300 milímetros, la vía efectiva mide 190 y la separación entre pivotes delanteros es 120. Cada rueda mide 70 de diámetro y 26 de ancho. Al importar las mallas conservamos la forma del CAD y simplificamos las colisiones para el contacto con el suelo.»

## 4 · Modelo · 37 s

«La posición y el rumbo se definen en el punto medio del eje trasero. La velocidad angular es la velocidad longitudinal multiplicada por la curvatura. El ángulo de la rueda virtual resulta de la distancia entre ejes y esa curvatura. En una curva a la izquierda, la mangueta izquierda gira más que la derecha, mientras la rueda trasera derecha avanza más rápido. Limitamos las órdenes a un radio de al menos 0,556 metros.»

## 5 · Trayectoria y control · 40 s

«La referencia es una curva de Gerono de 15,29 metros. La giramos para que al iniciar el robot quede tangente a la ruta. En cada ciclo buscamos la posición del robot en una ventana local, de modo que el cruce central no cambie el orden de los dos lóbulos. Ubicamos el punto objetivo a 32 centímetros, calculamos la curvatura con Pure Pursuit y enviamos velocidad longitudinal y angular a Gazebo. El ciclo corre a 20 hertz y reduce la velocidad cerca de la meta.»

## 6 · Resultados · 44 s

«La gráfica compara la trayectoria de referencia con la pose observada del eje trasero. El Challenger completó los dos lóbulos y regresó al cruce. El error RMS resume la desviación durante la prueba. El máximo indica el punto de mayor separación y la distancia final se toma cuando el controlador envía la orden de parada. Esta corrida usa directamente la pose de Gazebo, así que las cifras describen el escenario simulado.»

«En la corrida grabada medimos 28,60 segundos simulados, 0,12 centímetros de error RMS y 0,33 centímetros de error máximo.»

## 7 · Aplicación · 29 s

«Proponemos una plataforma de inspección para un parque solar con pasillos pavimentados y retornos amplios. El robot puede recorrer filas largas y tomar la curva de retorno en avance. Las ruedas convencionales reducen el arrastre lateral frente al skid-steer en ese trazado. Si hay puntos estrechos, se debe revisar el espacio de maniobra desde la planificación.»

## 8 · Cierre · 37 s

Reproduce entre 8 y 12 segundos del video de Gazebo, por ejemplo el cruce entre los dos lóbulos. Continúa con el cierre.

«Comprobamos la integración del CAD, la simulación y el control de trayectoria. Para el siguiente ensayo proponemos variar la velocidad y la anticipación, calibrar el contacto de las ruedas y comparar la pose ideal con una estimación basada en encoders e IMU. Gracias.»

Exporten un MP4 de hasta cinco minutos y comprueben que cada participante aparece, que se entiende el audio y que el clip muestra el robot en movimiento. La grabación conjunta requiere la cámara de los integrantes.
