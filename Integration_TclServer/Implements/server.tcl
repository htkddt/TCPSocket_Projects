namespace eval ::noc {
	proc _get_local_host {} {
		if {$::tcl_platform(platform) eq "windows"} {
			set out [exec ipconfig]
			# regexp {IPv4 Address[^\:]*: ([0-9\.]+)} $out -> ip
			regexp {([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)} $out ip
		} else {
			set ip [exec hostname --long]
		}
		return $ip
	}
	
    # >>> Host, port, and socket handle
	# >>> Use function to get host name or IP address of host
	variable host [_get_local_host]
	# >>> Define IP address of host on Windows by ipconfig command
	# variable host "10.21.1.113"
	# >>> Script automatically reads IP address of host running this script on Linux
	# variable host [exec hostname --long]
    variable port 10001
	variable sock
	
	# >>> The list of clients
	variable clients {}

	# >>> Function check port before server is opened.
    proc _is_port_in_use {port} {
        set sock [catch {socket -server {} $port} result]
        if {$sock == 0} {
            close $result
            return 0
        }
        return 1
    }

	# >>> Routing messages between internal client and external client
    proc _process_one_line {channel} {
		variable clients
		if {[eof $channel]} {
			# >>> Remove client in the list
			set clients [lsearch -inline -not -exact $clients $channel]

			close $channel
			return
		}
		# >>> Read message
		set msg [gets $channel]
		if {$msg eq ""} {
			return
		}
		# >>> Forward message to all other clients
		foreach c $clients {
			if {$c ne $channel} {
				puts $c $msg
				flush $c
			}
		}
    }

	# >>> Handle event for connection both internal and external
    proc _on_client_connect {channel addr port} {
		variable clients
        gets $channel line
        fconfigure $channel -buffering line
		# >>> Save client into list
		lappend clients $channel
        fileevent $channel readable [namespace code "::noc::_process_one_line $channel"]
    }

	# >>> Function to receive data from external client to app
	proc _external_to_internal {sock} {
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
			if {[info commands qt_message] ne ""} {
				qt_message $line
			}
		}
	}

	# >>> Function to send data from app to external client (Called from C++)
	proc _internal_to_external {msg} {
		variable sock
		if {[info exists sock]} {
			puts $sock $msg
			flush $sock
		}
	}
	
	# >>> Establish connection for internal client
	proc _internal_client_connection {} {
		# Remove the control character. Ex: (\b) Backspace, (\r) Carriage Return
		fconfigure stdout -translation lf
		# puts "Starting Tcl socket client..."

		variable host
        variable port

		# >>> Make sock global so SendMessageToServer can use it
		variable sock

		# >>> Open connection to server
		set sock [socket $host $port]
		fconfigure $sock -blocking 0 -buffering line
		
		# >>> Register fileevent for async read
		fileevent $sock readable [list ::noc::_external_to_internal $sock]
	}

	# >>> Function to open server into application (The packet routing message between 2 clients)
    proc start {} {
        variable host
        variable port
        variable sock

        while {[_is_port_in_use $port]} {
            incr port
        }

        set sock [socket -server [namespace code ::noc::_on_client_connect] $port]
        set port [lindex [chan configure $sock -sockname] end]
    }

	# >>> Function to close server or disconnect the 2 clients when the application closes
    proc stop {} {
        # variable cfg_file_path
        variable host
        variable port
        variable sock

        if {![info exists sock]} return
		
		# puts "Closing Tcl socket client."

        close $sock
        unset sock

        # if {![file exists $cfg_file_path]} return

        # set cfg_file [open $cfg_file_path r]
        # set lines [split [read $cfg_file] "\n"]
        # close $cfg_file

        # set updated_lines [list]
        # foreach line $lines {
            # if {$line != "" && ![string match $host,$port,* $line]} {
                # lappend updated_lines $line
            # }
        # }

        # set cfg_file [open $cfg_file_path w]
        # foreach line $updated_lines {
            # puts $cfg_file $line
        # }
        # close $cfg_file
    }    
}
