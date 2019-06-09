#include "SignalHandler.h"
#include "signal.h"

using namespace std;

bool SignalHandler::m_signalSet = false;

SignalHandler::SignalHandler()
{
}

SignalHandler::~SignalHandler()
{
}

bool SignalHandler::setSignalToHandle(int sig)
{
    if(signal(sig, SignalHandler::setSignal) == SIG_ERR) {
        return false;
    }
    return true;
}

void SignalHandler::setSignal(int unused)
{
    m_signalSet = true;
}

bool SignalHandler::isSignalSet()
{
    return m_signalSet;
}
