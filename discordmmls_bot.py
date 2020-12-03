from asyncio.locks import Semaphore
from datetime import date, datetime, timedelta
import mmlsattendance
import discord
from discord.ext import commands
from io import StringIO  # import string IO to print whole string
import asyncio
import aiohttp

# DO NOT SHARE

bot = commands.Bot(
    command_prefix=["Pls ", "Please ", "please ", "pls ", "PLS ", "!"])
global_semaphore = asyncio.Semaphore(12)  # the number of allowable task
discordid_to_subjectdatabase = {}
# file = StringIO()

# obtain ctx value from the attendance task

'''TO-DO'''

"""1. pls login "id no" - utk login. then nanti dia mintak password
2. pls qr - kalau nak link attendance utk class harini
3. pls search date "yyyy-mm-dd" - kalau nak link attendance utk specific date
4. pls sign - kalau nak login attendance semua class harini sekaligus
kredit to : @japer"""

'''Pls user rosak'''

'''mantap, dah boleh main valo'''

''''sabar sikit woi!'''

'''nak paksa masuk tak ?'''

'''aku dah ada password kau :smirk::smirk:
mantul la per
nanti tolong hack valorant sekali'''

'''buat pilihan ❌'''


async def printTodiscord_process(ctx, queue, found_dates=set()):
    while True:
        object1 = await queue.get()
        embed_message = discord.Embed(
            title=f"{object1.subject_code} - {object1.subject_name}", url=object1.attendance_url, colour=discord.Colour.blue(),
            description=f"{object1.class_code} | {object1.class_date} | {object1.start_time}-{object1.end_time}\n[{ctx.author.mention}]"
        )
        await ctx.send(embed=embed_message)
        found_dates.add(date.fromisoformat(object1.class_date))
        queue.task_done()


async def scrapeattendance(ctx, SubjectDB_obj, timetableordate_start, timetableordate_end, found_dates):
    queue = asyncio.Queue()
    task = asyncio.create_task(printTodiscord_process(ctx, queue, found_dates))
    # search by timetable id
    if isinstance(timetableordate_start, int) and isinstance(timetableordate_end, int):
        await mmlsattendance.scrape(SubjectDB_obj, timetableordate_start, timetableordate_end, queue=queue, semaphore=global_semaphore)
    else:  # search by dates
        await mmlsattendance.scrape_date(SubjectDB_obj, timetableordate_start, timetableordate_end, queue=queue, semaphore=global_semaphore)
    await queue.join()
    task.cancel()
    await asyncio.wait([task])


async def class_today(ctx, queue, found_dates=set(), file=StringIO()):
    # format = "%A, %d %B"
    while True:
        object2 = await queue.get()
        # dateformat = (object2.class_date).strftime(format)
        print(f"{object2.subject_code} - {object2.subject_name}\t({object2.start_time}-{object2.end_time}, {object2.class_date})", file=file)
        found_dates.add(date.fromisoformat(object2.class_date))
        queue.task_done()


async def display_class(ctx, SubjectDB_obj, date_start, date_end, found_dates, file=StringIO()):
    queue = asyncio.Queue()
    # file = StringIO()
    # task here in parentheses
    task = asyncio.create_task(class_today(
        ctx, queue, found_dates, file))
    await mmlsattendance.scrape_date(SubjectDB_obj, date_start, date_end, queue=queue, semaphore=global_semaphore)
    await queue.join()
    task.cancel()
    await asyncio.wait([task])

### in development #######


async def force_sign(ctx, queue, date_register, starttime_register, endtime_register, student_id, student_password, file):
    while True:
        object3 = await queue.get()
        status = await mmlsattendance.sign_now(
            object3.attendance_url, object3.class_id, date_register, starttime_register, endtime_register, object3.timetable_id, student_id, student_password, semaphore=global_semaphore)
        print(f"{object3.subject_code} - {object3.subject_name}\n{status}\n", file=file)
        queue.task_done()


async def force_sign_attendance(ctx, SubjectDB_obj, date_start, date_end, date_register, starttime_register, endtime_register, mmuid, mmupassword, file):
    queue = asyncio.Queue()
    task = asyncio.create_task(force_sign(
        ctx, queue, date_register, starttime_register, endtime_register, mmuid, mmupassword, file))  # Make task here
    await mmlsattendance.scrape_date(SubjectDB_obj, date_start, date_end, queue=queue, semaphore=global_semaphore)
    await queue.join()
    task.cancel()
    await asyncio.wait([task])

##############
#
# async def print_timetable():  # prototype
#    pass
#    return


@ bot.command()  # loads registered subjects and classes from mmls (finish)
async def login(ctx, studentid=None, password=None):  # change here
    if ctx.author.id in discordid_to_subjectdatabase:
        await ctx.send(f"Eh...I think you've login before? 😵")
        return
    else:
        subjectdatabase = mmlsattendance.SubjectDB()  # class for storing database
        dm_channel = await ctx.author.create_dm() or ctx.author.dm_channel
        if studentid == None:
            await ctx.send(f"DM me your `MMLS credentials`. 🤔")
        elif studentid != None:
            await ctx.send(f"DM me your `MMLS password`. 🤐")
        await dm_channel.send(f"Beep Boop, I'm an MMLS bot from {ctx.message.channel.mention}, {ctx.message.guild.name}. 🤖")
        for wrongpass in range(3):
            if studentid == None:
                for i in range(5):
                    try:
                        studentidmsg = await bot.wait_for("message", check=lambda x: x.author == ctx.author, timeout=7)
                        studentid = studentidmsg.content
                        break
                    except asyncio.TimeoutError:
                        if i == 0:
                            await dm_channel.send(f"Reply with your `MMU Student ID` or `cancel` if you change your mind.")
                            continue
                        elif i == 3:
                            await dm_channel.send(f"Hellooo? Are you there? 😩")
                            continue
                        elif i == 4:
                            await dm_channel.send("Im leaving you. 🤬")
                            await ctx.send(f"{ctx.author.mention} didn't notice me. 😭")
                            return
                # studentid = studentidmsg.content
                if studentid.lower() == "cancel":
                    await dm_channel.send(f"Changed your mind, huh? I'm leaving. 😑")
                    return
                else:
                    await dm_channel.send(f"Your `MMLS password`?")
                    try:
                        password = await bot.wait_for("message", check=lambda x: x.author == ctx.author, timeout=15)
                    except asyncio.TimeoutError:
                        await dm_channel.send("Ghosted me halfway? Fine, I'm leaving.👻")
                        return
            elif studentid != None:
                for i in range(5):
                    try:
                        # , check = lambda x: x.channel == dm_channel
                        password = await bot.wait_for("message", check=lambda x: x.author == ctx.author, timeout=8)
                        break
                    except asyncio.TimeoutError:
                        if i == 0:
                            await dm_channel.send(f"Reply with your `MMLS password` or `cancel` if you change your mind.")
                            continue
                        elif i == 4:
                            await dm_channel.send("Not willing to give your MMLS password ya? I'm leaving. 🙄")
                            return
                # await ctx.send(content = password.content) #send password from dm to general chat in server
            password = password.content
            if password.lower() == "cancel":
                await dm_channel.send(f"Changed your mind, huh? I'm leaving. 😑")
                return
            else:
                await dm_channel.send("Lemme' access the MMLS... 🌏")
                async with ctx.channel.typing():
                    # this function returns True or False value
                    if await mmlsattendance.load_online(subjectdatabase, studentid, password, semaphore=global_semaphore):
                        # can go back to channel
                        await dm_channel.send(f"Done! You can go back to {ctx.message.channel.mention}. 😎")
                        break
                    else:
                        if wrongpass == 0:
                            await dm_channel.send("Please check your `Student ID` or `MMLS password`. Let's try again from the start.\n\nWhat's your `MMU StudentID`?")
                            studentid = None
                            continue
                        elif wrongpass == 1:
                            await dm_channel.send("Heads in the clouds? Let's try again from the start.\n\nWhat's your `MMU StudentID`?")
                            await ctx.send("Someone is forgetting their MMLS credentials. 😏")
                            studentid = None
                            continue
                        else:
                            await dm_channel.send("Try to remember your MMLS credentials. Goodbye. I'm leaving. 😒")
                            await ctx.send(f"{ctx.author.mention} forgot their MMLS credentials. 🤣🤣🤣")
                            return
        async with ctx.channel.typing():
            await mmlsattendance.autoselect_classes(subjectdatabase, studentid, semaphore=global_semaphore)
            if subjectdatabase.selected_classes:
                discordid_to_subjectdatabase.update(
                    {ctx.author.id: {"StudentID": studentid}}
                )
                discordid_to_subjectdatabase[ctx.author.id].update(
                    {"StudentPassword": password})
                discordid_to_subjectdatabase[ctx.author.id].update(
                    {"SubjectDB": subjectdatabase})  # subjectdatabase is a class
                await ctx.send(f"{ctx.author.mention}, I've obtain all your registered subjects from MMLS. ✅")
                print(
                    f"{ctx.author} >>> {discordid_to_subjectdatabase[ctx.author.id]['StudentID']}")
                return
            else:
                await ctx.send(f"{ctx.author.mention}, I'm having trouble to obtain all your registered classes. Try again in a bit. 😥")
                return


## code for status bot command ##
@ bot.command(aliases=["users"])  # finish
async def user(ctx):
    ("\nList of user(s) that is currently using the bot.\n")
    if discordid_to_subjectdatabase:
        printlist = "User(s) below are currently using the MMLS service: 🧐\n"
        for i, discordid in enumerate(discordid_to_subjectdatabase.keys()):
            printlist += f"\n{i+1}.) <@{discordid}> >>> `{discordid_to_subjectdatabase[ctx.author.id]['StudentID']}`"
        # await ctx.send(f"```{discorduserlist.getvalue()}```")
        await ctx.send(f"{printlist}\n\nDo logout after using the service.")
        return
    else:
        await ctx.send(f"I'm lonely. There's no one using my service. 😢")
        # {discordid_to_subjectdatabase[ctx.author.id]}
        return


@ bot.command()  # finish
async def logout(ctx):
    ("\nForgets the subjects and classes of the calling user.\n")
    try:
        discordid_to_subjectdatabase.pop(ctx.author.id)
        await ctx.send(f"Poof, I've forgotten all your subjects {ctx.author.mention}. 🤓")
        return
    except KeyError:  # happens when user tries to access a key that is not in dictionary, in this context its ctx.author.id
        await ctx.send(f"You weren't even logged in... 🌚")
        return


## need to check for bugs and error ##
@ bot.command(aliases=["qr", "QR", "link", "links"])
async def attendance(ctx):  # attendance link for today class
    ("\nGives the attendance of all today class for the calling user.\n")
    if ctx.author.id in discordid_to_subjectdatabase:
        attendance_date_or_url = None
        # attendance_enddate = None
        SubjectDB_obj = discordid_to_subjectdatabase[ctx.author.id]["SubjectDB"]
        try:
            if attendance_date_or_url is None:
                format = "%A, %d %B"
                printAttendance_date = (datetime.now()).strftime(
                    format)  # date for today
                attendance_date_or_url = (datetime.now()).date()
            else:
                attendance_date_or_url = date.fromisoformat(
                    attendance_date_or_url)  # receive inputs of yyyy-mm-dd format
        except ValueError:
            await ctx.send("Me dumb. Gib me in yyyy-mm-dd format pwease? 🥴")
            return
        found_dates = set()  # found_dates = set()
        # refer line 191 discordbot
        await ctx.send(f"Looking for attendance today. 📡 __{printAttendance_date}__")
        async with ctx.typing():
            try:
                await scrapeattendance(ctx, SubjectDB_obj, attendance_date_or_url, attendance_date_or_url, found_dates)
            except aiohttp.ClientError as Error:
                await ctx.send("There's problem connecting to the MMLS. Try again later. 🌏")
                print(f"MMLS server problem. {Error}")
                return
        # print(found_dates)
        if not found_dates:
            await ctx.send(f"You sure there's class today? Try asking for attendance when there's class. 👀\n{ctx.author.mention}")
            return
        else:
            await ctx.send(f"{ctx.author.mention} Your attendance link(s) for today. 😴")
            return
    else:
        await ctx.send(f"❌Obtaining and tampering with attendance URLs without going to the class is wrong and should be penalized.❌\n.\n.\n.\nLog in first will ya? 🤫")
        return


@bot.group(aliases=["search", "Search"])
async def scrape(ctx):  # prototype
    ("\nHelp here.\n")
    if ctx.invoked_subcommand is None:
        await ctx.send(f"Search what, by dates or timetable ID? 🤡")


# best way to search for attendance
@scrape.command(aliases=["ttid", "timetable_id"])
async def timetableid(ctx, start_timetable, end_timetable):  # finish
    if ctx.author.id in discordid_to_subjectdatabase:
        SubjectDB_obj = discordid_to_subjectdatabase[ctx.author.id]["SubjectDB"]
        found_dates = set()
        try:
            start_timetable, end_timetable = int(
                start_timetable), int(end_timetable)
        except TypeError:
            await ctx.send(f"Huh? I need integers. Can I have integers with that command?")
        await ctx.send(f"Searching timetable from {start_timetable} to {end_timetable}... 📡")
        async with ctx.channel.typing():
            try:
                await scrapeattendance(ctx, SubjectDB_obj, start_timetable, end_timetable, found_dates)
            except aiohttp.ClientError:
                # if MMLS server got problem retrieving the attendance
                await ctx.send("There's problem connecting to the MMLS. Try again later. 📡")
                print(aiohttp.ClientError)
                return
        if found_dates == set():
            await ctx.send("No attendance link(s) found. 👀")
            return
        else:
            await ctx.send(f"Done! That's all the attendance from {start_timetable} to {end_timetable}. 😉")
            return
    else:
        await ctx.send(f"❌Obtaining and tampering with attendance URLs without going to the class is wrong and should be penalized.❌\n.\n.\n.\nLog in first will ya? 🤫")
        return


@timetableid.error  # finish for now
async def timetableid_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"I think you left out something. Maybe a missing argument? 🥱")
        return
    else:  # elif to check other type of error
        return


@scrape.command(name="date")  # search attendance by date (finish)
async def _date(ctx, attendance_startdate=None, attendance_enddate=None):
    if ctx.author.id in discordid_to_subjectdatabase:
        SubjectDB_obj = discordid_to_subjectdatabase[ctx.author.id]["SubjectDB"]
        found_dates = set()
        try:
            if attendance_startdate is None:
                attendance_startdate = attendance_enddate = (
                    (datetime.now()).date()
                )
            elif attendance_enddate is None:
                attendance_enddate = attendance_startdate = (
                    date.fromisoformat(attendance_startdate)
                )
            elif attendance_startdate and attendance_enddate is not None:
                attendance_startdate = date.fromisoformat(attendance_startdate)
                attendance_enddate = date.fromisoformat(attendance_enddate)
            else:
                attendance_startdate = date.fromisoformat(attendance_startdate)
                attendance_enddate = date.fromisoformat(attendance_enddate)
        except ValueError:
            await ctx.send(f"Me dumb. Gib me in yyyy-mm-dd format pwease? 🥴")
            return
        # """if attendance_startdate is None and attendance_enddate is None:
        #    attendance_startdate = (datetime.now()).date()  # date for today
        # else:
        #    attendance_startdate = date.fromisoformat(
        #        attendance_startdate)  # receive inputs of yyyy-mm-dd format"""
        if attendance_startdate != attendance_enddate:  # print if attendance is a range
            await ctx.send(f"Looking for attendance from {attendance_startdate.isoformat()} to {attendance_enddate.isoformat()}. 📡")
        elif attendance_startdate == attendance_enddate:  # print if search only one date
            await ctx.send(f"Looking for attendance on the date {attendance_startdate.isoformat()}. 📡")
        async with ctx.typing():
            await scrapeattendance(ctx, SubjectDB_obj, attendance_startdate, attendance_enddate, found_dates)
            for date_num in (attendance_startdate + timedelta(days=d) for d in range((attendance_enddate-attendance_startdate).days+1)):
                # discard from found date date_num so it be empty
                found_dates.discard(date_num)
        if not found_dates:  # if found dates is empty, go here
            if attendance_startdate != attendance_startdate:
                await ctx.send(f"Here's the attendance from {attendance_startdate} to {attendance_enddate}, I guess. 😬")
            elif attendance_startdate == attendance_enddate:
                await ctx.send(f"Here's the attendance for the date {attendance_startdate}, I guess. 😬")
            return
        else:
            await ctx.send(f"Hrmm, I've probably missed some attendance URLs due to technical issue. Try using the timetable ID range search instead. 😅")
            return
    else:
        await ctx.send(f"❌Obtaining and tampering with attendance URLs without going to the class is wrong and should be penalized.❌\n.\n.\n.\nLog in first will ya? 🤫")
        return


@bot.command(name="class")
async def print_subjects(ctx):
    ("""\nDisplay stored subjects, classes and selection.\n""")
    if ctx.author.id in discordid_to_subjectdatabase:
        SubjectDB_obj = discordid_to_subjectdatabase[ctx.author.id]['SubjectDB']
        with StringIO() as f:
            num_pad = len(str(len(SubjectDB_obj.subjects)))
            space = ' '*num_pad + ' '*2
            cat_space = space + ' '*3
            for subject_no, subject in enumerate(SubjectDB_obj.subjects, 1):
                subj_no = str(subject_no).rjust(num_pad)
                print(f"{subj_no}. {subject.code} - {subject.name}",
                      file=f)        # 1. ECE2056 - DATA COMM AND NEWORK
                print(f"{space}> Subject ID: {subject.id}",
                      file=f)  # > Subject ID: 232
                # > Coordinator ID: 1577623541
                print(f"{space}> Coordinator ID: {subject.coordinator_id}", file=f)
                print(f"{cat_space}Sel Class Class ID",
                      file=f)  # Sel Class Class ID
                # a. [X]  EC01    45132
                for char_id, kelas in enumerate(subject.classes, ord('a')):
                    X = 'X' if kelas.selected else ' '  # b. [ ]  ECA1    45172
                    print(
                        f"{space}{chr(char_id)}. [{X}]{kelas.code:>6}{kelas.id:>9}", file=f)
                if subject_no != len(SubjectDB_obj.subjects):
                    print('', file=f)
            await ctx.channel.send(f"Here's your registered subjects and their classes:\n```{f.getvalue()}```")
    else:
        await ctx.send(f"❌Obtaining and tampering with attendance URLs without going to the class is wrong and should be penalized.❌\n.\n.\n.\nLog in first will ya? 🤫")
        return


@bot.command()
async def aiman(ctx):
    ctx.send()


@ bot.command()  # Prototype
async def sign(ctx, attendance_date_or_url=None):  # here???
    if ctx.author.id in discordid_to_subjectdatabase:
        # attendance_date_or_url = None
        # attendance_enddate = None
        SubjectDB_obj = discordid_to_subjectdatabase[ctx.author.id]["SubjectDB"]
        try:
            if attendance_date_or_url is None:  # try to detect Value error here
                format = "%A, %d %B"
                printAttendance_date = (datetime.now()).strftime(
                    format)  # date for today
                attendance_date_or_url = (datetime.now()).date()
            elif len(str(attendance_date_or_url)) <= 11:
                attendance_date_or_url = date.fromisoformat(
                    attendance_date_or_url)  # receive inputs of yyyy-mm-dd format
                format = "%A, %d %B"
                printAttendance_date = attendance_date_or_url.strftime(format)
            else:
                async with ctx.typing():
                    check_link_func = await mmlsattendance.checkmmls_link(attendance_date_or_url, SubjectDB_obj)
                    check_link = check_link_func[0]

                    if check_link == True:
                        # continue with sign in
                        scraped_mmls = check_link_func[1]
                        student_id = discordid_to_subjectdatabase[ctx.author.id]["StudentID"]
                        student_password = discordid_to_subjectdatabase[ctx.author.id]["StudentPassword"]
                        starttime_register = datetime.now() - timedelta(hours=1)
                        endtime_register = datetime.now() + timedelta(hours=1)
                        starttime_register = (starttime_register.time()).isoformat(
                            timespec="seconds")
                        endtime_register = (endtime_register.time()).isoformat(
                            timespec="seconds")
                        attendancedate_register = (datetime.now()).date()
                        with StringIO() as file:
                            print(
                                f"{scraped_mmls.subject_code} - {scraped_mmls.subject_name}\t({scraped_mmls.start_time}-{scraped_mmls.end_time}, {scraped_mmls.class_date})", file=file)
                            msg_here = await ctx.send(f"```{file.getvalue()}```")
                            await msg_here.add_reaction("✅")
                            await ctx.send("Do you want to force-sign-in this attendance? 😈")
                        try:
                            await bot.wait_for('reaction_add', timeout=60, check=lambda reaction, user: reaction.emoji == '✅' and user == ctx.message.author)
                        except asyncio.TimeoutError:
                            await ctx.send("Ghosted me? Boohoo. 👻")
                            return
                        status = await mmlsattendance.sign_now(
                            scraped_mmls.attendance_url, scraped_mmls.class_id, attendancedate_register, starttime_register, endtime_register, scraped_mmls.timetable_id, student_id, student_password, semaphore=global_semaphore)
                        await ctx.send(f"```{status}```")
                        await ctx.send("Done!")
                        # print(scraped_mmls.timetable_id)
                        return
                    elif await mmlsattendance.checkmmls_link(attendance_date_or_url, SubjectDB_obj) == False:
                        await ctx.send("it is MMLS attendance link but not registered class")
                        return
                    elif await mmlsattendance.checkmmls_link(attendance_date_or_url, SubjectDB_obj) == attendance_date_or_url:
                        await ctx.send("It is a link but not an MMLS attendance link")
                        return
                    else:
                        await ctx.send("Not a link/giberrish")
                        return
        except ValueError:
            await ctx.send("Me dumb. Gib me in yyyy-mm-dd format pwease? 🥴")
            return
        found_dates = set()  # found_dates = set()
        async with ctx.typing():
            try:  # Func. that scrape #
                with StringIO() as file:
                    await display_class(ctx, SubjectDB_obj, attendance_date_or_url, attendance_date_or_url, found_dates, file)
                    if file.getvalue() != None:
                        stringio_class = await ctx.send(f"```{file.getvalue()}```")
                        await stringio_class.add_reaction("✅")
                    elif file.getvalue() == None:
                        pass
                # await stringio_class.add_reaction("❌") PROTOTYPE
            except aiohttp.ClientError as Error:
                await ctx.send("There's problem connecting to the MMLS. Try again later. 🌏")
                print(f"MMLS server problem. 🖥 {Error}")
                return
        if not found_dates:
            await ctx.send(f"There's no class on the date you've mentioned. Try again when there's class. 👀\n{ctx.author.mention}")
            return
        else:
            # await ctx.send(f"{ctx.author.mention} Your class for __{printAttendance_date}__. 😴")
            await ctx.send(f"Force-sign-in attendance(s) link? ")

            # def check(reaction, user):
            #    return user == ctx.message.author and str(reaction.emoji == '✅')

            try:
                await bot.wait_for('reaction_add', timeout=60, check=lambda reaction, user: reaction.emoji == '✅' and user == ctx.message.author)
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention} Ghosted me halfway eh? Boohoo. 👻")
                return
            else:
                async with ctx.typing():
                    await ctx.send("Please wait! 💤")
                    mmuid = discordid_to_subjectdatabase[ctx.author.id]["StudentID"]
                    mmupassword = discordid_to_subjectdatabase[ctx.author.id]["StudentPassword"]
                    starttime_register = datetime.now() - timedelta(hours=1)
                    endtime_register = datetime.now() + timedelta(hours=1)
                    starttime_register = (starttime_register.time()).isoformat(
                        timespec="seconds")
                    endtime_register = (endtime_register.time()).isoformat(
                        timespec="seconds")
                    attendancedate_register = (datetime.now()).date()
                    with StringIO() as file:
                        await force_sign_attendance(ctx, SubjectDB_obj, attendance_date_or_url, attendance_date_or_url, attendancedate_register, starttime_register, endtime_register, mmuid, mmupassword, file)
                        await ctx.channel.send(f"```{file.getvalue()}```")
                await ctx.send("Success. You can go back to sleep now. 😴")
                return
            # return  # continue to event/command listener
    else:
        await ctx.send((f"❌Obtaining and tampering with attendance URLs without going to the class is wrong and should be penalized.❌\n.\n.\n.\nLog in first will ya? 🤫"))
        return


@ bot.event
async def on_ready():  # finish
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="MMU"))
    print(f"Logged in as {bot.user}")
    for guild_list, guild in enumerate(bot.guilds, 1):
        print(f"-> {guild.id}: {guild.name}")
    print(f"Bot is in {guild_list} server.")


bot.run("NzcwOTg0MTUwNzYwMDMwMjE4.X5lg8Q.jtTApoeN1bY3crR6VOK2dYJfNGQ")
