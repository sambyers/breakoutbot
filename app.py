'''Simple bot to automate making random breakout groups in a Webex team.'''
import logging
from flask import Flask, request
from webexteamssdk import WebexTeamsAPI, Webhook


app = Flask(__name__)
wbxapi = WebexTeamsAPI()
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def rm_member_from_list(members: list) -> object:
    try:
        return members.pop(0)
    except(IndexError) as e:
        logger.exception(e)
        return None


def add_member_to_room(member: object, room: object) -> object:
    logger.info(f'Adding {member.personDisplayName} to {room.title}...')
    return wbxapi.memberships.create(room.id, personId=member.personId)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return 'OK. This is the break_out_bot!'
    if request.method == 'POST':
        webhook_obj = Webhook(request.get_json())
        room = wbxapi.rooms.get(webhook_obj.data.roomId)
        message = wbxapi.messages.get(webhook_obj.data.id)
        me = wbxapi.people.me()
        if message.personId == me.id:
            # Message was sent by me (bot); do not respond.
            logger.info('Not responding to self.')
            return 'OK. Not responding to self.'
        try:
            team = wbxapi.teams.get(room.teamId)
        except(TypeError) as e:
            logger.error(f'Error: {e}')
            wbxapi.messages.create(
                room.id,
                markdown="Oh no! 😵 It seems this space isn't part of a **team**. "
                "I can only work within a **team**. "
                )
        if team:
            command_list = message.text.split(' ')
            if 'help' in command_list[1]:
                wbxapi.messages.create(
                    room.id,
                    markdown=f"Hello! 👋 I'm B.O.B the break_out_bot! Currently, I'm aware of the team **{team.name}**. \n"
                    "\nCommands available:\n"
                    "- **help**: Shows this help text.\n"
                    "- **breakout n**: Create breakout spaces and add _n_ number of team members to it.\n"
                    "- **cleanup**: Archive any breakout spaces that were created by me."
                    )
            elif 'breakout' in command_list[1]:
                breakout_size = int(command_list[2])
                team_memberships = wbxapi.team_memberships.list(team.id)
                team_members = [member for member in team_memberships if not member.personId == me.id]
                team_member_count = len(team_members)
                team_room_number = int(team_member_count/breakout_size)
                team_member_names = [member.personDisplayName for member in team_members]
                wbxapi.messages.create(
                    room.id,
                    markdown=f"Creating breakout teams for: {', '.join(team_member_names)}"
                    )
                for i in range(team_room_number+1):
                    if len(team_members) > 0:
                        new_room = wbxapi.rooms.create(f"BOB_Breakout Space #{i+1}", teamId=team.id)
                        logger.info(f'Created room {new_room.title}.')
                        wbxapi.messages.create(
                            room.id,
                            markdown=f"Created breakout space {new_room.title}."
                            )
                        wbxapi.messages.create(
                            new_room.id,
                            markdown=f"Welcome to {new_room.title}!"
                            )
                        if len(team_members) < breakout_size:
                            for m in team_members:
                                add_member_to_room(m, new_room)
                        else:
                            for i in range(breakout_size):
                                m = rm_member_from_list(team_members)
                                add_member_to_room(m, new_room)
                    # Remove bot from new room, but disables cleanup.
                    # bot_membership = wbxapi.memberships.list(roomId=new_room.id, personId=me.id)
                    # for bot in bot_membership:
                    #     wbxapi.memberships.delete(bot.id)
            elif 'cleanup' in command_list[1]:
                breakout_rooms = wbxapi.rooms.list(teamId=team.id)
                for r in breakout_rooms:
                    if 'BOB_Breakout' in r.title:
                        wbxapi.messages.create(
                            room.id,
                            markdown=f"Cleaning up breakout space {r.title}."
                            )
                        wbxapi.rooms.delete(r.id)
                wbxapi.messages.create(
                    room.id,
                    markdown="Cleaning up finished! 🥳."
                    )
        return 'OK'


if __name__ == '__main__':
    app.run()
