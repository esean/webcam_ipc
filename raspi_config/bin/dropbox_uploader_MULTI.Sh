#!/bin/bash

die() { echo "ERROR:$0:$@ !"; exit 1; }
warn() { echo "WARNING:$0:$@"; }
usage() {
	echo
	echo "USAGE: $0 {[-r]} [Dropbox dest folder] [files to sync]"
	echo
	echo "FLAGS:"
	echo "	-r	remove files once uploaded"
	echo
}

rm_after=0
case X"$1" in
	X-h|X--help)	usage; exit 0;;
	X-r)		rm_after=1;shift;;
esac
[ -z "$2" ] && die "`usage`"
dest="$1"; shift

# check destination dir exists on dropbox
dropbox_uploader.sh list $dest &> /dev/null
[ ! $? -eq 0 ] && warn "Dropbox directory '$dest' does not exist, creating..."

# copy all files in that dir
ret=0
for fn in $@; do
	[ ! -f "$fn" ] && {
		warn "File '$fn' does not exist, skipping..." 
	continue
	}

	bn="$(basename $fn)"
	cmd="dropbox_uploader.sh upload $fn $dest/$bn"
#	echo "#DEBUG: cmd=$cmd"
	$cmd || ret=1

	# REMOVE ORIGINAL FILE (only if requested with '-r' option)
	[ $rm_after -eq 1 ] && rm -f $fn
done

exit $ret

