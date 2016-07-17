
### Summary: Individuals ###
	 > Randy Smith (@I1@ - line 15)
		 * Gender: Male (line 20)
		 * Birth date: 9 FEB 1992 (line 22)
		 * Current age: 24.45
		 * Child in: Family (@F1@ - line 133)
	 > Jacob Smith (@I2@ - line 24)
		 * Gender: Male (line 29)
		 * Birth date: 6 AUG 1960 (line 31)
		 * Current age: 55.99
		 * Spouses: Caroll Rodriguez (@I3@ - line 35), Rita Jones (@I9@ - line 92)
		 * Spouse in: Family (@F1@ - line 133), Family (@F2@ - line 139)
		 * Child in: Family (@F3@ - line 144)
	 > Caroll Rodriguez (@I3@ - line 35)
		 * Gender: Female (line 40)
		 * Birth date: 15 JAN 1968 (line 42)
		 * Current age: 48.54
		 * Spouses: Jacob Smith (@I2@ - line 24)
		 * Spouse in: Family (@F1@ - line 133)
		 * Child in: Family (@F4@ - line 149)
	 > Rachel Smith (@I4@ - line 45)
		 * Gender: Female (line 50)
		 * Birth date: 17 AUG 1994 (line 52)
		 * Current age: 21.93
		 * Child in: Family (@F1@ - line 133)
	 > Greg Smith (@I5@ - line 54)
		 * Gender: Male (line 59)
		 * Birth date: 18 NOV 1937 (line 61)
		 * Death date: 3 FEB 2007 (line 63)
		 * Age at death: 69.26
		 * Spouses: Marry Anderson (@I6@ - line 65)
		 * Spouse in: Family (@F3@ - line 144)
	 > Marry Anderson (@I6@ - line 65)
		 * Gender: Female (line 70)
		 * Birth date: 6 JAN 1938 (line 72)
		 * Current age: 78.58
		 * Spouses: Greg Smith (@I5@ - line 54)
		 * Spouse in: Family (@F3@ - line 144)
	 > Frank Rodriguez (@I7@ - line 74)
		 * Gender: Male (line 79)
		 * Birth date: 3 FEB 1943 (line 81)
		 * Current age: 73.5
		 * Spouses: Sammy Santiago (@I8@ - line 83)
		 * Spouse in: Family (@F4@ - line 149)
	 > Sammy Santiago (@I8@ - line 83)
		 * Gender: Female (line 88)
		 * Birth date: 10 MAY 1947 (line 90)
		 * Current age: 69.24
		 * Spouses: Frank Rodriguez (@I7@ - line 74)
		 * Spouse in: Family (@F4@ - line 149)
	 > Rita Jones (@I9@ - line 92)
		 * Gender: Female (line 97)
		 * Birth date: 6 JAN 1964 (line 99)
		 * Death date: 7 JUL 1983 (line 101)
		 * Age at death: 19.51
		 * Spouses: Jacob Smith (@I2@ - line 24)
		 * Spouse in: Family (@F2@ - line 139)
		 * Child in: Family (@F5@ - line 154)
	 > Mike Jones (@I10@ - line 104)
		 * Gender: Male (line 109)
		 * Birth date: 7 FEB 1940 (line 111)
		 * Death date: 10 APR 2012 (line 113)
		 * Age at death: 72.22
		 * Spouses: Aubry Conan (@I11@ - line 115)
		 * Spouse in: Family (@F5@ - line 154)
	 > Aubry Conan (@I11@ - line 115)
		 * Gender: Female (line 120)
		 * Birth date: 5 JAN 1945 (line 122)
		 * Current age: 71.58
		 * Spouses: Mike Jones (@I10@ - line 104)
		 * Spouse in: Family (@F5@ - line 154)
	 > Frank Smith (@I12@ - line 124)
		 * Gender: Male (line 129)
		 * Birth date: 6 APR 1988 (line 131)
		 * Current age: 28.3
		 * Child in: Family (@F2@ - line 139)

### Summary: Families ###
	 > Family (@F1@ - line 133)
		 * Husband: Jacob Smith (@I2@ - line 24)
		 * Wife: Caroll Rodriguez (@I3@ - line 35)
		 * Child 1: Randy Smith (@I1@ - line 15)
		 * Child 2: Rachel Smith (@I4@ - line 45)
	 > Family (@F2@ - line 139)
		 * Husband: Jacob Smith (@I2@ - line 24)
		 * Wife: Rita Jones (@I9@ - line 92)
		 * Child 1: Frank Smith (@I12@ - line 124)
	 > Family (@F3@ - line 144)
		 * Husband: Greg Smith (@I5@ - line 54)
		 * Wife: Marry Anderson (@I6@ - line 65)
		 * Child 1: Jacob Smith (@I2@ - line 24)
	 > Family (@F4@ - line 149)
		 * Husband: Frank Rodriguez (@I7@ - line 74)
		 * Wife: Sammy Santiago (@I8@ - line 83)
		 * Child 1: Caroll Rodriguez (@I3@ - line 35)
	 > Family (@F5@ - line 154)
		 * Husband: Mike Jones (@I10@ - line 104)
		 * Wife: Aubry Conan (@I11@ - line 115)
		 * Child 1: Rita Jones (@I9@ - line 92)

### Error US01: Dates Before Current Date ###
~~~~
[failed]
~~~~

### Error US02: Birth Before Marriage ###
~~~~
[failed]
~~~~

### Error US03: Birth Before Death ###
~~~~
[failed]
~~~~

### Error US04: Marriage Before Divorce ###
~~~~
[failed]
~~~~

### Error US05: Marriage Before Death ###
~~~~
[failed]
~~~~

### Error US06: Divorce Before Death ###
~~~~
[failed]
~~~~

### Error US07: Less Then 150 Years Old ###
~~~~
[failed]
~~~~

### Anomaly US08: Birth Before Marriage Of Parents ###
~~~~
[failed]
~~~~

### Error US09: Birth Before Death Of Parents ###
~~~~
[failed]
	 > Family (@F2@ - line 139) has Child Frank Smith (@I12@ - line 124) with birth date 6 APR 1988 (line 131) and has mother Rita Jones (@I9@ - line 92) with death date 7 JUL 1983 (line 101) and father Jacob Smith (@I2@ - line 24) with no death date.
	 > Family (@F3@ - line 144) has Child Jacob Smith (@I2@ - line 24) with birth date 6 AUG 1960 (line 31) and has mother Marry Anderson (@I6@ - line 65) with no death date and father Greg Smith (@I5@ - line 54) with death date 3 FEB 2007 (line 63).
	 > Family (@F5@ - line 154) has Child Rita Jones (@I9@ - line 92) with birth date 6 JAN 1964 (line 99) and has mother Aubry Conan (@I11@ - line 115) with no death date and father Mike Jones (@I10@ - line 104) with death date 10 APR 2012 (line 113).
~~~~

### Anomaly US10: Marriage After 14 ###
~~~~
[failed]
~~~~

### Anomaly US11: No Bigamy ###
~~~~
[failed]
~~~~

### Anomaly US12: Parents Not Too Old ###
~~~~
[failed]
~~~~

### Anomaly US13: Siblings Spacing ###
~~~~
[failed]
~~~~

### Anomaly US14: Less Than 5 Multiple Births ###
~~~~
[failed]
~~~~

### Anomaly US15: Fewer Than 15 Siblings ###
~~~~
[failed]
~~~~

### Anomaly US16: Male Last Names ###
~~~~
[failed]
~~~~

### Anomaly US17: No Marriages To Descendants ###
~~~~
[failed]
~~~~
