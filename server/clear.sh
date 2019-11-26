#!/bin/bash
psql -U cryptophone -d cryptophone -c "delete from messages where true; delete from phonebook where true;"
