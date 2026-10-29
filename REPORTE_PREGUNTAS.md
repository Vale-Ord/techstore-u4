1. **¿Por qué Decimal y no float?** 
Se utiliza Decimal porque permite trabajar con cantidades de dinero de forma más exacta. En cambio, float guarda los números en binario y puede generar pequeños errores en los decimales.

2. **Renglones vs unidades.** 
Los renglones son las líneas que aparecen en un pedido, mientras que las unidades son la suma de las cantidades de todos los productos. 

3. **Ventaja de Specification.** 
La ventaja es que cada regla se guarda en un objeto con un nombre específico, como VIPCustomerSpec o MinimumUnitsSpec, lo que permite probarlas por separado, reutilizarlas y combinarlas según lo que se necesite. De esta manera, se evita repetir muchos if en diferentes partes del código.

4. **Eventos solo tras transición válida.** 
Los eventos sirven para avisar que algo ya ocurrió, por lo que primero se debe comprobar que la operación sea válida. Si se registrara un evento antes de hacer esa validación, se podría indicar que algo sucedió cuando en realidad la operación fue rechazada.

5. **Qué se reutiliza si cambia FastAPI.** 
Se podría reutilizar casi todo el código relacionado con la lógica del sistema, como app/domain.py, app/specifications.py y cargar_csv.py, porque estas partes no dependen de FastAPI ni de las solicitudes HTTP. Esto permite seguir utilizando las entidades, las reglas, los estados y la carga de datos aunque se cambie la interfaz.

# Reflexión
Durante la realización del proyecto se encontraron algunos errores que nos ayudaron a entender mejor cómo funciona el entorno y la API. El primero fue cuando PowerShell no permitía activar el entorno virtual porque la ejecución de scripts estaba deshabilitada. Lo solucionamos utilizando el comando Set-ExecutionPolicy -Scope CurrentUser RemoteSigned y aprendimos que Windows tiene estas restricciones por seguridad y que se pueden ajustar para nuestro usuario.

Tuvimos tambien un error accidental que fué escribir 0013 con ceros en lugar de O013 con la letra O al buscar un pedido en Swagger. Esto provocó un error 404 porque el sistema no encontró el identificador. Con este error entendimos la importancia de escribir correctamente los IDs y comprobamos que la API responde cuando se busca un pedido que no existe.

Otro error fue cuando intentamos confirmar el mismo pedido dos veces, apareció un error 409 y al principio pensamos que algo estaba fallando. Después vimos que era el comportamiento esperado, porque el pedido ya estaba confirmado y no podía volver a realizarse la misma transición. Con este error vimos que los estados se guardan en memoria, por lo que se reinician cuando se apaga el servidor.