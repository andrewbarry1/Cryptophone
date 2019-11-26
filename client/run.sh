if [ "$1" == "clear" ]; then
	rm *.txt
elif [ "$1" == "wipe" ]; then
	rm -rf users/*
	rm *.txt
fi
python3 client.py
