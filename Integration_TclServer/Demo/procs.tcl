namespace eval ::noc {

    # Configuration file path
    variable cfg_file_path [file normalize "$::env(HOME)/.ns_host_config"]

    # Host, port, and socket handle
    variable host [exec hostname --long]
    variable port 10001
    variable sock
    variable done
	
	# The list of clients
	set clients {}


    proc _is_port_in_use {port} {
        set sock [catch {socket -server {} $port} result]
        if {$sock == 0} {
            close $result
            return 0
        }
        return 1
    }


    proc _eval_line {channel line} {
        puts "$channel cmd: $line"
        flush stdout
        if {[catch {
            eval $line
        } error]} {
            puts $error
            flush stdout
            puts $channel "ERROR: $error"
            flush $channel
        } else {
            puts $channel "ACK: Command processed successfully"
            flush $channel
        }
    }


    proc _process_one_line {channel} {
        puts "Process one line."

		global clients
		if {[eof $channel]} {
			puts "Client disconnected"

			# Remove client in the list
			set clients [lsearch -inline -not -exact $clients $channel]

			close $channel
			return
		}
		# Read message
		set msg [gets $channel]
		if {$msg eq ""} {
			return
		}
		# Forward message to all other clients
		foreach c $clients {
			if {$c ne $channel} {
				puts $c $msg
				flush $c
			}
		}
    }


    proc _on_client_connect {channel addr port} {
		global clients
        puts "On client connect: $channel."
        gets $channel line
        fconfigure $channel -buffering line
		# Save client into list
		lappend clients $channel
        fileevent $channel readable [namespace code "_process_one_line $channel"]
    }


    variable timeout_event_loop


    proc start {} {
        variable cfg_file_path
        variable host
        variable port
        variable sock
        variable done

        while {[_is_port_in_use $port]} {
            incr port
        }

        set sock [socket -server [namespace code _on_client_connect] $port]
        set port [lindex [chan configure $sock -sockname] end]

        file mkdir [file dirname $cfg_file_path]
        set cfg_file [open $cfg_file_path a]
        puts $cfg_file "$host,$port,[pid]"
        close $cfg_file

        puts "Server started on $host:$port."

        package require Tk
        wm withdraw .
        toplevel .top
        wm protocol .top WM_DELETE_WINDOW [namespace code {set done 1}]
        button .top.b -text "Stop Server" -command [namespace code {set done 1}]
        pack .top.b
        vwait [namespace which -variable done]
        destroy .top
        update

        stop
    }


    proc stop {} {
        variable cfg_file_path
        variable host
        variable port
        variable sock

        if {![info exists sock]} return

        close $sock
        unset sock

        if {![file exists $cfg_file_path]} return

        set cfg_file [open $cfg_file_path r]
        set lines [split [read $cfg_file] "\n"]
        close $cfg_file

        set updated_lines [list]
        foreach line $lines {
            if {$line != "" && ![string match $host,$port,* $line]} {
                lappend updated_lines $line
            }
        }

        set cfg_file [open $cfg_file_path w]
        foreach line $updated_lines {
            puts $cfg_file $line
        }
        close $cfg_file

        puts "Server stopped and port $port removed from config file."
    }


    proc redirect {filename cmd} {
        try {
            set mode w
            set destination [open $filename $mode]
        } on error {} {
            uplevel $cmd
            return
        }

        rename ::puts ::tcl::orig::puts
        proc ::puts args "uplevel \"::tcl::orig::puts $destination \$args\"; return"

        try {
            uplevel $cmd
        } on error { result } {
            close $destination
            rename ::puts {}
            rename ::tcl::orig::puts ::puts
            error $result
        }

        close $destination
        rename ::puts {}
        rename ::tcl::orig::puts ::puts
    }
    
}
