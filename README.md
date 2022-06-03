#Friendshiplamps

###Zusammenfassung
Zwei physisch getrennte Lampen sollen zeitgleich
aktiviert, bzw. deaktiviert werden können.

###Komponenten
Die Komponenten sind ein Raspberry Pi, der Knopf und ein relay, welches über die 
GPIO-Pins angesprochen wird

###Eingabe
Die Eingabe erfolg mit den GPIO-Pins am Pi.

###Kommunikation
Die Kommunikation erfolg via einen MQTT-Server, welcher mit den Path
in der Config deklariert wird. Der Path ist der konfigurierte
MQTT-Path, sowie die beiden Clientnamen als Sub-Path auf welchen der eine Client
die Nachricht veröffentlicht und der andere die Nachricht abboniert.