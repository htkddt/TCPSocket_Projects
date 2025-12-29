#include "TclSocketServer.h"
#include <QTimer>
#include <QDebug>

TclSocketServer::TclSocketServer(Tcl_Interp* interp, QObject* parent) : _interp(interp), QObject(parent) {
    // Register callback command Tcl → C++
    Tcl_CreateObjCommand(_interp, "qt_message", QtMessageCmd, this, nullptr);

    // Process Tcl events periodically (non-blocking)
    QTimer* eventTimer = new QTimer(this);
    connect(eventTimer, &QTimer::timeout, this, &TclSocketServer::processTclEvents);
    eventTimer->start(10);
}

TclSocketServer::~TclSocketServer() {
    if (_interp) {
        Tcl_DeleteInterp(_interp);
        _interp = nullptr;
    }
}

bool TclSocketServer::init(const QString& scriptPath) {
    if (!_interp) return false;

    QByteArray pathUtf8 = scriptPath.toUtf8();
    if (Tcl_EvalFile(_interp, pathUtf8.constData()) == TCL_ERROR) {
        qCritical() << "Error running Tcl script:" << Tcl_GetStringResult(_interp);
        return false;
    }
    return true;
}

bool TclSocketServer::start() {
    if (!_interp) return false;
    if (Tcl_Eval(_interp, "::noc::start") == TCL_ERROR) return false;
    isStarted = true;
    return true;
}

bool TclSocketServer::setConnection() {
    if (!_interp) return false;
    if (Tcl_Eval(_interp, "::noc::_internal_client_connection") == TCL_ERROR) return false;
    return true;
}

bool TclSocketServer::stop() {
    if (!_interp) return false;
    if (Tcl_Eval(_interp, "::noc::stop") == TCL_ERROR) return false;
    isStarted = false;
    return true;
}

void TclSocketServer::processTclEvents() {
    while (Tcl_DoOneEvent(TCL_DONT_WAIT)) {
        // Tcl handles socket readable/file events internally
    }
}

void TclSocketServer::sendMessageToClient(const QString& msg) {
    if (!_interp) return;

    QString cmd = QString("::noc::_internal_to_external {%1}").arg(msg);
    QByteArray cmdUtf8 = cmd.toUtf8();
    if (Tcl_Eval(_interp, cmdUtf8.constData()) == TCL_ERROR) {
        qWarning() << "Send message failed ---> [ERROR]:" << Tcl_GetStringResult(_interp);
    }
}

int TclSocketServer::QtMessageCmd(ClientData clientData, Tcl_Interp* interp, int objc, Tcl_Obj* const objv[]) {
    auto* engine = static_cast<TclSocketServer*>(clientData);
    if (objc >= 2 && engine) {
        QString msg = Tcl_GetString(objv[1]);
        emit engine->messageReceived(msg);
    }
    return TCL_OK;
}
