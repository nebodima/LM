﻿
&НаКлиенте
Процедура Обновить(Команда)
	ОбновитьНаСервере();
КонецПроцедуры

Процедура ОбновитьНаСервере()
	Справочники.ИдентификаторыОбъектовМетаданных.ОбновитьДанныеСправочника(Истина);
КонецПроцедуры

