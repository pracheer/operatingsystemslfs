Tasks completed:
1. Fix sync : DONE (included in general tests)
2. Fix File Descriptor Write : DONE (included in general tests)
3. Fix file search : DONE (included in general tests)
4. Write block to segment : DONE (included in general tests)
5. Test and play : DONE (included in general tests)
6. Deletion : DONE (included in general tests)
7. Indirect Blocks : DONE (included in general tests)
8. Extra Credit: Relative Filenames : DONE (included in general tests)
9. Extra Credit: Cleaner (not able to test)
10. Extra Credit: Multithread support : DONE (test process mentioned below)
11. Extra Credit: Mailserver Integration : DONE (test process mentioned below)


Default filesystem.bin is updated to run check MAIL SERVER INTEGRATION
(i.e. it includes the directory /mails/pracheer.gupta@gmail.com and /mails/pg298@cornell.edu)


Note to run tests:

TO CHECK MAIL SERVER INTEGRATION:
in LFS create a directory /mails which would contain directories for each of the user with their email ids:
(pg298@cornell.edu and pracheer.gupta@gmail.com).

E.g.
[LFS] /mails> ls
.	inode=2	type=DIR	size=128
..	inode=1	type=DIR	size=64
pg298@cornell.edu	inode=3	type=DIR	size=96
pracheer.gupta@gmail.com	inode=4	type=DIR	size=64

indicating LFS had mails for two email accounts.

do sync
[LFS] /mails> sync
then exit
[LFS] /mails> exit

Then run email_server.py
Then run email_client_1.py
one new file would be created in pracheer.gupta@gmail.com directory with timestamp as its name.
Then run email_client_2.py
one new file would be created in pg298@cornell.edu directory with timestamp as its name.


TO CHECK MULTITHREADING:
Run TestMultiThreading.py
2 threads will be created each of which would be creating a bunch of files and directories and its subdirectories till the 3rd level.
(if currently a shell is running, then it should be 'exit'ed and reopened with 'mkfs -reuse' to see all the effects).


TO RUN SOME GENERAL TESTS:
Run Test.py
one file of size 102500 (using an indirect block) will be created in /long_file.txt
one temp directory would be created with one temporary file.