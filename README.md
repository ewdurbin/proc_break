# proc_break

This is the first Python program I ever wrote.

## Story

At the time I was working on a new Linux/MySQL/Apache/PHP (LAMP) stack
application with a team of three or four people.

Our lead on the project decided to implement all database action via stored
procedures, which was _great_ except for we had no idea when these things were
changing or why.

With vigor, I set forth to figure out how to extract the stored procedure
definitions and get them committed to version control.

If I recall correctly, the first hit for "scripted access to mysql" was a
tutorial using a Python MySQL adapter, so I started down that path.

Eventually connecting straight to the database didn't work out, but having
already written some Python, I just stuck with that.

Nine years later, here we are.
