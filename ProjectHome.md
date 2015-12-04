Pypk is a Python implementation of a port knocking system application, a method used to dynamically open a specified port on a server in case that a certain IP attempts to send packets on a set of prespecified ports.
Once a correct sequence of connection is received by the "knock daemon", in a certain amount of time, the firewall rules table is dynamically modified to allow the "knocker" to connect over a certain port(s).
Generally, port knocking is most often used to determine access to port 22, the Secure Shell (SSH) port, but can also be used to hide other "private" services like TELNET, VNC and many others.

For more information see: http://billiejoex.altervista.org/Prj_Py_port_knock.htm