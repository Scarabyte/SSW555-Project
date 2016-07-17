
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
[passed]
	 > Individual Randy Smith (@I1@ - line 15) has a birth date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Birth date is 9 FEB 1992 (line 22)
	 > Individual Jacob Smith (@I2@ - line 24) has a birth date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Birth date is 6 AUG 1960 (line 31)
	 > Individual Caroll Rodriguez (@I3@ - line 35) has a birth date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Birth date is 15 JAN 1968 (line 42)
	 > Individual Rachel Smith (@I4@ - line 45) has a birth date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Birth date is 17 AUG 1994 (line 52)
	 > Individual Greg Smith (@I5@ - line 54) has a birth date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Birth date is 18 NOV 1937 (line 61)
	 > Individual Greg Smith (@I5@ - line 54) has a death date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Death date is 3 FEB 2007 (line 63)
	 > Individual Marry Anderson (@I6@ - line 65) has a birth date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Birth date is 6 JAN 1938 (line 72)
	 > Individual Frank Rodriguez (@I7@ - line 74) has a birth date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Birth date is 3 FEB 1943 (line 81)
	 > Individual Sammy Santiago (@I8@ - line 83) has a birth date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Birth date is 10 MAY 1947 (line 90)
	 > Individual Rita Jones (@I9@ - line 92) has a birth date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Birth date is 6 JAN 1964 (line 99)
	 > Individual Rita Jones (@I9@ - line 92) has a death date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Death date is 7 JUL 1983 (line 101)
	 > Individual Mike Jones (@I10@ - line 104) has a birth date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Birth date is 7 FEB 1940 (line 111)
	 > Individual Mike Jones (@I10@ - line 104) has a death date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Death date is 10 APR 2012 (line 113)
	 > Individual Aubry Conan (@I11@ - line 115) has a birth date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Birth date is 5 JAN 1945 (line 122)
	 > Individual Frank Smith (@I12@ - line 124) has a birth date before the current date
		 * Current Date is 17 JUL 2016 (date script ran)
		 * Birth date is 6 APR 1988 (line 131)
[failed]
~~~~

### Error US02: Birth Before Marriage ###
~~~~
[passed]
[failed]
~~~~

### Error US03: Birth Before Death ###
~~~~
[passed]
	 > Individual Greg Smith (@I5@ - line 54) born 18 NOV 1937 (line 61) before his death on 3 FEB 2007 (line 63)
	 > Individual Rita Jones (@I9@ - line 92) born 6 JAN 1964 (line 99) before her death on 7 JUL 1983 (line 101)
	 > Individual Mike Jones (@I10@ - line 104) born 7 FEB 1940 (line 111) before his death on 10 APR 2012 (line 113)
[failed]
~~~~

### Error US04: Marriage Before Divorce ###
~~~~
[passed]
[failed]
~~~~

### Error US05: Marriage Before Death ###
~~~~
[passed]
[failed]
~~~~

### Error US06: Divorce Before Death ###
~~~~
[passed]
[failed]
~~~~

### Error US07: Less Then 150 Years Old ###
~~~~
[passed]
	 > Individual Randy Smith (@I1@ - line 15) was born 9 FEB 1992 (line 22) and is 24.45 years old as of 17 JUL 2016 (current date)
	 > Individual Jacob Smith (@I2@ - line 24) was born 6 AUG 1960 (line 31) and is 55.99 years old as of 17 JUL 2016 (current date)
	 > Individual Caroll Rodriguez (@I3@ - line 35) was born 15 JAN 1968 (line 42) and is 48.54 years old as of 17 JUL 2016 (current date)
	 > Individual Rachel Smith (@I4@ - line 45) was born 17 AUG 1994 (line 52) and is 21.93 years old as of 17 JUL 2016 (current date)
	 > Individual Greg Smith (@I5@ - line 54) was born 18 NOV 1937 (line 61) and died 69.26 years later on 3 FEB 2007 (line 63)
	 > Individual Marry Anderson (@I6@ - line 65) was born 6 JAN 1938 (line 72) and is 78.58 years old as of 17 JUL 2016 (current date)
	 > Individual Frank Rodriguez (@I7@ - line 74) was born 3 FEB 1943 (line 81) and is 73.5 years old as of 17 JUL 2016 (current date)
	 > Individual Sammy Santiago (@I8@ - line 83) was born 10 MAY 1947 (line 90) and is 69.24 years old as of 17 JUL 2016 (current date)
	 > Individual Rita Jones (@I9@ - line 92) was born 6 JAN 1964 (line 99) and died 19.51 years later on 7 JUL 1983 (line 101)
	 > Individual Mike Jones (@I10@ - line 104) was born 7 FEB 1940 (line 111) and died 72.22 years later on 10 APR 2012 (line 113)
	 > Individual Aubry Conan (@I11@ - line 115) was born 5 JAN 1945 (line 122) and is 71.58 years old as of 17 JUL 2016 (current date)
	 > Individual Frank Smith (@I12@ - line 124) was born 6 APR 1988 (line 131) and is 28.3 years old as of 17 JUL 2016 (current date)
[failed]
~~~~

### Anomaly US08: Birth Before Marriage Of Parents ###
~~~~
[passed]
[failed]
~~~~

### Error US09: Birth Before Death Of Parents ###
~~~~
[passed]
	 > Family (@F1@ - line 133) has Child Randy Smith (@I1@ - line 15) with birth date 9 FEB 1992 (line 22) and has mother Caroll Rodriguez (@I3@ - line 35) with no death date and father Jacob Smith (@I2@ - line 24) with no death date.
	 > Family (@F1@ - line 133) has Child Rachel Smith (@I4@ - line 45) with birth date 17 AUG 1994 (line 52) and has mother Caroll Rodriguez (@I3@ - line 35) with no death date and father Jacob Smith (@I2@ - line 24) with no death date.
	 > Family (@F4@ - line 149) has Child Caroll Rodriguez (@I3@ - line 35) with birth date 15 JAN 1968 (line 42) and has mother Sammy Santiago (@I8@ - line 83) with no death date and father Frank Rodriguez (@I7@ - line 74) with no death date.
[failed]
	 > Family (@F2@ - line 139) has Child Frank Smith (@I12@ - line 124) with birth date 6 APR 1988 (line 131) and has mother Rita Jones (@I9@ - line 92) with death date 7 JUL 1983 (line 101) and father Jacob Smith (@I2@ - line 24) with no death date.
	 > Family (@F3@ - line 144) has Child Jacob Smith (@I2@ - line 24) with birth date 6 AUG 1960 (line 31) and has mother Marry Anderson (@I6@ - line 65) with no death date and father Greg Smith (@I5@ - line 54) with death date 3 FEB 2007 (line 63).
	 > Family (@F5@ - line 154) has Child Rita Jones (@I9@ - line 92) with birth date 6 JAN 1964 (line 99) and has mother Aubry Conan (@I11@ - line 115) with no death date and father Mike Jones (@I10@ - line 104) with death date 10 APR 2012 (line 113).
~~~~

### Anomaly US10: Marriage After 14 ###
~~~~
[passed]
[failed]
~~~~

### Anomaly US11: No Bigamy ###
~~~~
[passed]
[failed]
~~~~

### Anomaly US12: Parents Not Too Old ###
~~~~
[passed]
[failed]
~~~~

### Anomaly US13: Siblings Spacing ###
~~~~
[passed]
	 > Family (@F1@ - line 133) has siblings born more than 8 months apart (920 days)
		 * Sibling Randy Smith (@I1@ - line 15) born 9 FEB 1992 (line 22)
		 * Sibling Rachel Smith (@I4@ - line 45) born 17 AUG 1994 (line 52)
[failed]
~~~~

### Anomaly US14: Less Than 5 Multiple Births ###
~~~~
[passed]
	 > Family (@F1@ - line 133) has no more than 5 siblings born on the same date, with 1 sibling born on 9 FEB 1992
		 * Sibling Randy Smith (@I1@ - line 15) born 9 FEB 1992 (line 22)
	 > Family (@F1@ - line 133) has no more than 5 siblings born on the same date, with 1 sibling born on 17 AUG 1994
		 * Sibling Rachel Smith (@I4@ - line 45) born 17 AUG 1994 (line 52)
	 > Family (@F2@ - line 139) has no more than 5 siblings born on the same date, with 1 sibling born on 6 APR 1988
		 * Sibling Frank Smith (@I12@ - line 124) born 6 APR 1988 (line 131)
	 > Family (@F3@ - line 144) has no more than 5 siblings born on the same date, with 1 sibling born on 6 AUG 1960
		 * Sibling Jacob Smith (@I2@ - line 24) born 6 AUG 1960 (line 31)
	 > Family (@F4@ - line 149) has no more than 5 siblings born on the same date, with 1 sibling born on 15 JAN 1968
		 * Sibling Caroll Rodriguez (@I3@ - line 35) born 15 JAN 1968 (line 42)
	 > Family (@F5@ - line 154) has no more than 5 siblings born on the same date, with 1 sibling born on 6 JAN 1964
		 * Sibling Rita Jones (@I9@ - line 92) born 6 JAN 1964 (line 99)
[failed]
~~~~

### Anomaly US15: Fewer Than 15 Siblings ###
~~~~
[passed]
	 > Family (@F1@ - line 133) has 2 siblings
		 * Child 1: Randy Smith (@I1@ - line 15)
		 * Child 2: Rachel Smith (@I4@ - line 45)
	 > Family (@F2@ - line 139) has one child
		 * Child 1: Frank Smith (@I12@ - line 124)
	 > Family (@F3@ - line 144) has one child
		 * Child 1: Jacob Smith (@I2@ - line 24)
	 > Family (@F4@ - line 149) has one child
		 * Child 1: Caroll Rodriguez (@I3@ - line 35)
	 > Family (@F5@ - line 154) has one child
		 * Child 1: Rita Jones (@I9@ - line 92)
[failed]
~~~~

### Anomaly US16: Male Last Names ###
~~~~
[passed]
	 > Family (@F1@ - line 133) with father Jacob Smith (@I2@ - line 24) and son Randy Smith (@I1@ - line 15) have the same surname
	 > Family (@F2@ - line 139) with father Jacob Smith (@I2@ - line 24) and son Frank Smith (@I12@ - line 124) have the same surname
	 > Family (@F3@ - line 144) with father Greg Smith (@I5@ - line 54) and son Jacob Smith (@I2@ - line 24) have the same surname
[failed]
~~~~

### Anomaly US17: No Marriages To Descendants ###
~~~~
[passed]
	 > Individual Jacob Smith (@I2@ - line 24) is not married to any of his children
	 > Individual Jacob Smith (@I2@ - line 24) is not married to any of his children
	 > Individual Jacob Smith (@I2@ - line 24) is not married to any of his children
	 > Individual Jacob Smith (@I2@ - line 24) is not married to any of his children
	 > Individual Caroll Rodriguez (@I3@ - line 35) is not married to any of her children
	 > Individual Greg Smith (@I5@ - line 54) is not married to any of his children
	 > Individual Marry Anderson (@I6@ - line 65) is not married to any of her children
	 > Individual Frank Rodriguez (@I7@ - line 74) is not married to any of his children
	 > Individual Sammy Santiago (@I8@ - line 83) is not married to any of her children
	 > Individual Rita Jones (@I9@ - line 92) is not married to any of her children
	 > Individual Mike Jones (@I10@ - line 104) is not married to any of his children
	 > Individual Aubry Conan (@I11@ - line 115) is not married to any of her children
[failed]
~~~~
