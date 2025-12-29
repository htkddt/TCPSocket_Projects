set host "10.116.181.184"
set port 10001

global sock

set sock [socket $host $port]
fconfigure $sock -buffering line -translation lf
fconfigure stdin -buffering line

puts "Connected to $host:$port"

proc onServerRead {} {
    global sock
    if {[eof $sock]} {
        puts "\nServer closed connection"
        close $sock
        exit
    }
    set msg [gets $sock]
    puts "Server: $msg"
}

fileevent $sock readable onServerRead

proc onUserInput {} {
    global sock
    if {[eof stdin]} {
        close $sock
        exit
    }
    set msg [gets stdin]
    puts $sock $msg
    flush $sock
}

fileevent stdin readable onUserInput

vwait forever
