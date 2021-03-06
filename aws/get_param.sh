#!/bin/bash


##############################################################################
##############################################################################
##
## MAGIC NUMBERS
##
##############################################################################
##############################################################################


ARG_NUMBER=1


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
        echo "  --name [Name of the SSM Parameter] \ "
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
            --name)
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

##############################################################################
##############################################################################
##
## MAIN
##
##############################################################################
##############################################################################


main(){

    aws ssm get-parameter --name $NAME --query Parameter.Value --output text --region 'us-east-1'

}


usage $@
parse_args $@

main

