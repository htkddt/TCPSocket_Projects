# Remove the control character. Ex: (\b) Backspace, (\r) Carriage Return
fconfigure stdout -translation lf
puts "Starting Tcl socket client..."

set host "10.116.22.180"
set port 10001

# Make sock global so SendMessageToServer can use it
global sock
# Open connection to server
set sock [socket $host $port]
fconfigure $sock -blocking 0 -buffering line

# Handle incoming data
proc onServerData {sock} {
    if {[eof $sock]} {
        puts "Connection closed by server"
        close $sock
        if {[info commands qt_message] ne ""} {
            qt_message "__CONNECTION_CLOSED__"
        }
        return
    }
    set line [gets $sock]
    if {$line ne ""} {
        #puts "$line\n"
        if {[info commands qt_message] ne ""} {
            qt_message $line
        }
    }
}

# Register fileevent for async read
fileevent $sock readable [list onServerData $sock]

# Function to send data to server (called from C++)
proc sendToServer {msg} {
    global sock
    if {[info exists sock]} {
        puts $sock $msg
        flush $sock
    }
}

