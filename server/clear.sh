#!/bin/bash
psql -U cryptophone -d cryptophone -c "delete from phonebook where true; delete from messages where true;"
