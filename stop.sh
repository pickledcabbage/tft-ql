#!/bin/bash

screen -S ql_frontend -X quit 2>/dev/null && echo "Stopped ql_frontend" || echo "ql_frontend not running"
screen -S ql_backend -X quit 2>/dev/null && echo "Stopped ql_backend" || echo "ql_backend not running"
