import nacl.utils
import nacl.pwhash
import getpass, os, json, base64, time
import clib # All general Cryptophone functionality (UI-independent)
from crypto import CryptoBox


# TODO this is probably very bad for security (ljust)
def prompt_pass(verify=False):
    pw = getpass.getpass().ljust(32).encode('utf-8')
    if verify:
        print('Enter password again')
        user_pw_check = prompt_pass(False)
        if not (pw == user_pw_check):
            raise Exception('Passwords do not match.')
        return user_pw_check
    return pw

def first_run():
    print('====== FIRST RUN ======')
    user_pw = prompt_pass(verify=True)
    clib.first_run(user_pw)
    phone_number = clib.first_run()
    print('====== YOU ARE ' + phone_number + ' ======')
    print('====== STARTUP COMPLETE ======')


def input_loop():
    if not os.path.isfile('id.txt'):
        first_run()
    try:
        chk_pw = prompt_pass()
    except:
        return
    if not(check_pw(chk_pw)):
        print("Incorrect password.")
        return

    Crypto = CryptoBox(chk_pw)
    dev_id = Crypto.decrypt_local('id.txt')
    pn = Crypto.decrypt_local('identity.txt')
    run = True
    while run:
        try:
            do_what = int(input("Do what? (1: Check msg, 2: Send msg, 3: Security, 4: Add Contact 5: Quit) "))
        except:
            break


        # Check messages
        if do_what == 1:
            from_u = input('From who? ')

            all_msgs_dec = clib.get_threaded_conversation(Crypto, dev_id, pn, from_u)
            if all_msgs_dec is None or len(all_msgs_dec) == 0:
                print('No messages from that number.')
            else:
                for msg in all_msgs_dec:
                    ts_format = time.strftime('%d/%m/%y %I:%M%p', time.gmtime(int(msg[0])))
                    if msg[1] == 0: # you sent this message
                        print(ts_format + ' (You)\n' + msg[2] + '\n\n')
                    else:
                        print(ts_format + '\n' + msg[2] + '\n\n')

        # Send message
        elif do_what == 2:
            to_u = input('To who? ')
            contents = input('Message: ')
            clib.send_message(Crypto, dev_id, pn, to_u, contents)
            print("Sent")
            
        elif do_what == 3:
            secu_prompt = int(input('(1: Change local password, 2: Regenerate keys, 3: Back) '))
            if secu_prompt == 1:
                new_pw = prompt_pass(True)
                clib.change_local_pw(Crypto, new_pw)
                print('Password changed')

            elif secu_prompt == 2:
                regen_prompt = input('This will erase all your old messages. Continue? ')
                if regen_prompt == 'y':
                    clib.regen_keys(Crypto)
                    print('Keys changed.')

        elif do_what == 4:
            name = input('What is their name? ')
            contact_pn = input('What is their number? ')
            clib.add_contact(Crypto, name, contact_pn)
            print('Added contact.')
            
            
        elif do_what == 5:
            run = False
            
if __name__=='__main__':
    input_loop()
