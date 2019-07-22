class SignalHandler
{
public:
    SignalHandler();
    ~SignalHandler();

    bool setSignalToHandle(int sig);
    static bool isSignalSet();
    static void setSignal(int unused);

private:
    static bool signalSet;

};