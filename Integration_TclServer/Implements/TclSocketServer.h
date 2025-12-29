#pragma once
#include <QObject>
#include "cpptcl/cpptcl.h"


class TclSocketServer : public QObject {
    Q_OBJECT
public:
    explicit TclSocketServer(Tcl_Interp*, QObject* parent = nullptr);
    ~TclSocketServer();

    bool init(const QString& scriptPath);
    bool start();
    bool setConnection();
    bool stop();
    bool getTclIsStartedState() { return isStarted; }
    bool isAutoOpenConnect() { return autoOpenConnect; }
    void setAutoOpenConnect(bool state) { autoOpenConnect = state; }
    void processTclEvents();
    void sendMessageToClient(const QString& msg);

signals:
    void messageReceived(const QString& msg);

private:
    static int QtMessageCmd(ClientData clientData, Tcl_Interp* interp, int objc, Tcl_Obj* const objv[]);
    Tcl_Interp* _interp = nullptr;
    bool isStarted = false;
    bool autoOpenConnect = false;
};
#pragma once
