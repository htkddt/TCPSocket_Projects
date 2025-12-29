set script_path [file dirname [info script]]

source [file join $script_path procs.tcl]

::noc::start
