import threading


def run_in_background(widget, work_fn, on_done):
    """Runs work_fn() (e.g. a DB query) off the main thread so the UI never
    freezes, then delivers the result back via .after() -- Tkinter widgets
    can only be touched from the main thread."""
    def target():
        try:
            result = work_fn()
        except Exception as e:
            result = e
        widget.after(0, lambda: on_done(result))

    threading.Thread(target=target, daemon=True).start()