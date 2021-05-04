#!/bin/bash


##############################################################################
##############################################################################
##
## MAGIC NUMBERS
##
##############################################################################
##############################################################################


ARG_NUMBER=1
REGION='us-east-1'

##############################################################################
##############################################################################
##
## USAGE
##
##############################################################################
##############################################################################


usage(){
    if [ $# -lt $ARG_NUMBER ]; then
        echo "Usage: "
        echo "$0 \ "
        echo "  --log-group-name [Name of the Cloudwatch Log Group] \ "
        exit 1
    fi
}


##############################################################################
##############################################################################
##
## PARSE ARGS
##
##############################################################################
##############################################################################


parse_args(){
    while [[ $# > 1 ]];
    do
        key="$1"

        case $key in
            --log-group-name)
            NAME="$2"
            shift # past argument
            ;;
            *)
            # unknown option
            ;;
        esac
        shift
    done
}


pretty_print() {
    str=$1
    num=$2
    v=$(printf "%-${num}s" "$str")
    echo "${v// /*}"
}

##############################################################################
##############################################################################
##
## MAIN
##
##############################################################################
##############################################################################


main(){

#    stream_query="logStreams[:10].[firstEventTimestamp,lastEventTimestamp,logStreamName]"
    stream_query="logStreams[0].[logStreamName]"

    stream_events=$(
        aws logs describe-log-streams \
            --log-group-name ${NAME} \
            --order-by LastEventTime \
            --region ${REGION} \
            --query ${stream_query} --output text
        )


#    echo $stream_events


    i=0
    for s in ${stream_events}; do

        if [ $i -gt 10 ]
        then
            break
        fi

        pretty_print "*" 79
        pretty_print "*" 2
        echo "** Log ${i} : ${s}"
        pretty_print "*" 2
        pretty_print "*" 79

        aws logs get-log-events \
            --log-group-name ${NAME} \
            --log-stream-name ${s} \
            --query "events[*].[timestamp,message]" --output text \
            --region ${REGION}

        i=$((++i))

    done



}


usage $@
parse_args $@

main

