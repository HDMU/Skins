ls *-fs8.png | cut -d " " -f8 > index.txt

		# Ermittle Zeilenanzahl der ipkg_list und setzte diese als Max 
		Zlistinstall=`wc -l index.txt | tr -s " " | cut -d " " -f1`
		ZeilenMax=`expr 1 "+" $Zlistinstall`
		Zeile=1 #Startzeile


		while [ $Zeile -lt $ZeilenMax ] ; do
			IPKG=`sed -n "$Zeile{p;q}" -- "index.txt"` > /dev/null
			ipkg=`sed -n "$Zeile{p;q}" -- "index.txt" | cut -d '-' -f1` > /dev/null
			mv $IPKG "$ipkg".png
			Zeile=`expr $Zeile "+" 1`
		done;
