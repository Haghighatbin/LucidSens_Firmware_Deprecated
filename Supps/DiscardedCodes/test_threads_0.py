import _thread

def usb_thread(arg):
    #print("TH_FUNC: started")
    # ------------------------------------------------------------
    # Allow suspending this thread from other threads using
    # _thread.suspend(th_id) / _thread.resume(th_id) functions.
    # If not set, the thread connot be suspended.
    # Still, "soft" suspend handling via notifications can be used
    # ------------------------------------------------------------
    _thread.allowsuspend(True)

    # ---------------------------------------------
    # Thread function usually runs in infinite loop
    # ---------------------------------------------
    while True:
        # ================================================
        # It is recommended to handle thread notifications
        # ================================================
        ntf = _thread.getnotification()
        if ntf:
            # some notification received
            if ntf == _thread.EXIT:
                # -------------------------------------------------
                # Return from thread function terminates the thread
                # -------------------------------------------------
                #print("TH_FUNC: terminated")
                return
            elif ntf == _thread.SUSPEND:
                # -------------------------------------------------------------------
                # The thread can be suspended using _thread.suspend(th_id) function,
                # but sometimes it is more convenient to implement the "soft" suspend
                # -------------------------------------------------------------------
                #print("TH_FUNC: suspended")
                # wait for RESUME notification indefinitely, some other thread must
                # send the resume notification: _thread.notify(th_id, _thread.RESUME)
                while _thread.wait() != _thread.RESUME:
                    pass
            # ---------------------------------------------
            # Handle the application specific notifications
            # ---------------------------------------------
            elif ntf == 1234:
                # Your notification handling code
                pass
            else:
                # -----------------------------
                # Default notification handling
                # -----------------------------
                pass

        try:
            cmd = sys.stdin.read(1)
            print(operator_func[cmd])
        except:
            return

        # ---------------------------------------------------------------------------
        # Thread function execution can be suspended until a notification is received
        # Without argument '_thread.wait' will wait for notification indefinitely
        # If the timeout argument is given, the function will return even if
        # no notification is received after the timeout expires with result 'None'
        # ---------------------------------------------------------------------------
        ntf = _thread.wait(30000)


        # typ, sender, msg = _thread.getmsg()
        # if msg:
        #     # -------------------------------------
        #     # message received from 'sender' thread
        #     # -------------------------------------
        #
        #     # Reply to sender, we can analyze the message first
        #     _thread.sendmsg(sender, "[%s] Hi %s, received your message." % (_thread.getSelfName(), _thread.getThreadName(sender)))
        #
        #     # We can inform the main MicroPython thread (REPL) about received message
        #     _thread.sendmsg(_thread.getReplID(), "[%s] Received message from '%s'\n'%s'" % (_thread.getSelfName(), _thread.getThreadName(sender), msg))