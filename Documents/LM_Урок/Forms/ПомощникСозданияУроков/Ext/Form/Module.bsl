﻿Функция ПолучитьВремяИзГруппы(Стр)
	
	Структ = Новый Структура;
	
	ГрВремяНачала = Неопределено;
	ГрВремяОкончания = Неопределено;
	
	ДеньНедели = Формат(Стр,"ДФ=ддд");
	Если ДеньНедели = "Пн" Тогда
		ГрВремяНачала = ?(ГруппаОбучения.ПН,ГруппаОбучения.ПНВремя,Неопределено);
		ГрВремяОкончания = ?(ГруппаОбучения.ПН,ГруппаОбучения.ПНВремя2,Неопределено);
	ИначеЕсли ДеньНедели = "Вт" Тогда
		ГрВремяНачала = ?(ГруппаОбучения.ВТ,ГруппаОбучения.ВТВремя,Неопределено);
		ГрВремяОкончания = ?(ГруппаОбучения.ВТ,ГруппаОбучения.ВТВремя2,Неопределено);
	ИначеЕсли ДеньНедели = "Ср" Тогда
		ГрВремяНачала = ?(ГруппаОбучения.СР,ГруппаОбучения.СРВремя,Неопределено);
		ГрВремяОкончания = ?(ГруппаОбучения.СР,ГруппаОбучения.СРВремя2,Неопределено);
	ИначеЕсли ДеньНедели = "Чт" Тогда
		ГрВремяНачала = ?(ГруппаОбучения.ЧТ,ГруппаОбучения.ЧТВремя,Неопределено);
		ГрВремяОкончания = ?(ГруппаОбучения.ЧТ,ГруппаОбучения.ЧТВремя2,Неопределено);
	ИначеЕсли ДеньНедели = "Пт" Тогда
		ГрВремяНачала = ?(ГруппаОбучения.ПТ,ГруппаОбучения.ПТВремя,Неопределено);
		ГрВремяОкончания = ?(ГруппаОбучения.ПТ,ГруппаОбучения.ПТВремя2,Неопределено);
	ИначеЕсли ДеньНедели = "Сб" Тогда
		ГрВремяНачала = ?(ГруппаОбучения.СБ,ГруппаОбучения.СБВремя,Неопределено);
		ГрВремяОкончания = ?(ГруппаОбучения.СБ,ГруппаОбучения.СБВремя2,Неопределено);
	ИначеЕсли ДеньНедели = "Вс" Тогда
		ГрВремяНачала = ?(ГруппаОбучения.ВС,ГруппаОбучения.ВСВремя,Неопределено);
		ГрВремяОкончания = ?(ГруппаОбучения.ВС,ГруппаОбучения.ВСВремя2,Неопределено);
	КонецЕсли;
	
	Если ЗначениеЗаполнено(ГрВремяНачала) и ЗначениеЗаполнено(ГрВремяОкончания) Тогда
		Структ.Вставить("ВремяНачала",ГрВремяНачала);
		Структ.Вставить("ВремяОкончания",ГрВремяОкончания);
		Возврат Структ;
	КонецЕсли;
		
	Возврат Неопределено; 	
	
КонецФункции

Процедура ВыполнитьНаСервере()
	
	Если НЕ УстановитьВремяВручную и ЗначениеЗаполнено(ГруппаОбучения) Тогда		
		Если Не ГруппаОбучения.ПН и Не ГруппаОбучения.ВТ и не ГруппаОбучения.СР и не ГруппаОбучения.ЧТ и не ГруппаОбучения.ПТ и не ГруппаОбучения.СБ и не ГруппаОбучения.ВС Тогда
			ТекстСообщения = "Не заполнено время по дням неделям в группе обучения!";
			ОбщегоНазначенияКлиентСервер.СообщитьПользователю(ТекстСообщения);
			Возврат;
		КонецЕсли; 		
	ИначеЕсли УстановитьВремяВручную Тогда 		
		Если Не ЗначениеЗаполнено(ВремяНачала) или Не ЗначениеЗаполнено(КоличествоЧасов) Тогда
			ТекстСообщения = "Не заполнено время начала или продолжительность!";
			ОбщегоНазначенияКлиентСервер.СообщитьПользователю(ТекстСообщения);
			Возврат;
		КонецЕсли; 		
	КонецЕсли;
	
	Если Элементы.Страницы.ТекущаяСтраница = Элементы.Страница1 Тогда	
		
		ИнформационнаяТЗ.Добавить().Описание = "--==СозданиеИлиДобавлениеВСуществующиеЗанятия " +ТекущаяДата();
		  
		Для Каждого Стр из Элементы.Календарь.ВыделенныеДаты Цикл
			
			//Если ЗначениеЗаполнено(ГруппаОбучения) Тогда
				Запрос = Новый Запрос;
				Запрос.Текст = 
				"ВЫБРАТЬ ПЕРВЫЕ 1
				|	Урок.Ссылка КАК Ссылка
				|ИЗ
				|	Документ.LM_Урок КАК Урок
				|ГДЕ
				|	Урок.Проведен = ИСТИНА
				//|	И Урок.ГруппаОбучения = &ГруппаОбучения
				|	И Урок.Окончание <= &ДатаОкончания
				//|	И Урок.Педагог = &Педагог
				|	И Урок.ПредметОбучения = &ПредметОбучения
				|	И Урок.Помещение = &Помещение
				|	И Урок.Дата >= &ДатаНачала";				
				Если ЗаполнятьИзГруппыОбучения Тогда
					СтруктураВременИзГруппы = ПолучитьВремяИзГруппы(Стр);
					Если СтруктураВременИзГруппы = Неопределено Тогда
						Продолжить;
					КонецЕсли;
					ВремяНачала = СтруктураВременИзГруппы.ВремяНачала;
					КоличествоЧасов = '00010101' + (СтруктураВременИзГруппы.ВремяОкончания - СтруктураВременИзГруппы.ВремяНачала);
				КонецЕсли;
				
				Запрос.УстановитьПараметр("ДатаНачала", Стр-('00010101'-ВремяНачала)); 
				Запрос.УстановитьПараметр("ДатаОкончания", Стр + 59 -('00010101'-ВремяНачала)-('00010101'-КоличествоЧасов));
				Запрос.УстановитьПараметр("ПредметОбучения", ПредметОбучения);
				//Запрос.УстановитьПараметр("Педагог", Педагог);
				Запрос.УстановитьПараметр("Помещение", Помещение);
				
				РезультатЗапроса = Запрос.Выполнить();				
				ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();
				
				Если ВыборкаДетальныеЗаписи.Количество() = 0 Тогда
					ДокС = Документы.LM_Урок.СоздатьДокумент();
					
					ВремяЗанятия 	= ВремяНачала;
					КолЧасов 		= КоличествоЧасов;
					
					ДокС.Дата 			 = Стр-('00010101'-ВремяЗанятия);
					ДокС.ПредметОбучения = ПредметОбучения;
					ДокС.Статус			 = СтатусУрока;
					ДокС.Педагог 		 = Педагог;
					Если НЕ Педагог.Пустая() Тогда
						ДокС.СтавкаПедагога  = Педагог.СтавкаПедагога;
					КонецЕсли;
					ДокС.Помещение 		 = Помещение;
					ДокС.ГруппаОбучения  = ГруппаОбучения;
					ДокС.Тариф  		 = Тариф;
					ДокС.КоличествоЧасов = КолЧасов;
					
					Для Каждого СтрУченик из Ученики Цикл
						Если Не ЗначениеЗаполнено(СтрУченик.Ученик) Тогда 
							Продолжить;
						КонецЕсли;
						НоваяСтрока = ДокС.Ученики.Добавить();
						НоваяСтрока.Ученик 			= СтрУченик.Ученик;
						НоваяСтрока.Тариф			= СтрУченик.Тариф;
						НоваяСтрока.Скидка			= СтрУченик.Скидка;
						НоваяСтрока.СписатьОплату 	= СтрУченик.СписатьОплату;
						НоваяСтрока.Явка 			= СтрУченик.Явка;
					КонецЦикла;
					
					Попытка
						Если Записывать Тогда
							ДокС.Записать(РежимЗаписиДокумента.Запись);
						Иначе
							ДокС.Записать(РежимЗаписиДокумента.Проведение);
						КонецЕсли;
						НовСтр = ИнформационнаяТЗ.Добавить();
						НовСтр.Урок = ДокС.Ссылка;
						НовСтр.Описание = "Создан";
					Исключение
						ИнформационнаяТЗ.Добавить().Описание = "Не удалось создать урок!";
					КонецПопытки;
					
				КонецЕсли;
				
				// Если урок уже существовал
				Пока ВыборкаДетальныеЗаписи.Следующий() Цикл
					
					ДокС = ВыборкаДетальныеЗаписи.Ссылка.ПолучитьОбъект();
					
					ДокИзменен = Ложь;
					
					Для Каждого СтрУченик из Ученики Цикл
						Если Не ЗначениеЗаполнено(СтрУченик.Ученик) Тогда 
							Продолжить; 
						КонецЕсли;
						
						УченикУжеПрисутствует = Ложь;
						Для Каждого Уч из ДокС.Ученики Цикл
							Если СтрУченик.Ученик = Уч.Ученик Тогда
								НовСтр = ИнформационнаяТЗ.Добавить();
								НовСтр.Описание = "Ученик "+СтрУченик.Ученик+" уже присутствует в уроке № " +ДокС.Номер+
								" от " +Формат(ДокС.Дата,"ДФ=dd.MM.yyyy")+ " с " +Формат(ДокС.Дата,"ДФ=HH:mm")+ " по " +Формат(ДокС.Окончание,"ДФ=HH:mm")+ ". Пропускаем...";
								НовСтр.Урок = ВыборкаДетальныеЗаписи.Ссылка;
								УченикУжеПрисутствует = Истина;
							КонецЕсли; 							
						КонецЦикла;
						
						Если УченикУжеПрисутствует Тогда
							Продолжить;
						КонецЕсли;
						
						НоваяСтрока = ДокС.Ученики.Добавить();
						НоваяСтрока.Ученик 			= СтрУченик.Ученик;
						НоваяСтрока.Тариф			= СтрУченик.Тариф;
						НоваяСтрока.Скидка			= СтрУченик.Скидка;
						НоваяСтрока.СписатьОплату 	= СтрУченик.СписатьОплату;
						НоваяСтрока.Явка 			= СтрУченик.Явка;
						
						ДокИзменен = Истина;
						
					КонецЦикла;
					
					Если ДокИзменен Тогда
						Попытка
							Если Записывать Тогда
								ДокС.Записать(РежимЗаписиДокумента.Запись);
							Иначе
								ДокС.Записать(РежимЗаписиДокумента.Проведение);
							КонецЕсли;							
							НовСтр = ИнформационнаяТЗ.Добавить();
							НовСтр.Описание = "Выполнено добавление учеников";
							НовСтр.Урок 	= ДокС.Ссылка;
						Исключение
							ИнформационнаяТЗ.Добавить().Описание = "Не удалось записать урок! " +ОписаниеОшибки();
						КонецПопытки;
					КонецЕсли;  				
					
				КонецЦикла;
			
		КонецЦикла;		
				
	ИначеЕсли ПродлениеГруппы Тогда
		
		ИнформационнаяТЗ.Добавить().Описание = "--==НАЧАЛО ПродлениеГруппы " +ТекущаяДата();
		
		Запрос = Новый Запрос;
		Запрос.Текст = 
		"ВЫБРАТЬ ПЕРВЫЕ 1
		|	Урок.Ссылка,
		|	Урок.Дата КАК Дата
		|ИЗ
		|	Документ.LM_Урок КАК Урок
		|ГДЕ
		|	Урок.Проведен = ИСТИНА
		|	И Урок.ГруппаОбучения = &ГруппаОбучения
		|
		|УПОРЯДОЧИТЬ ПО
		|	Дата УБЫВ
		|АВТОУПОРЯДОЧИВАНИЕ";
		
		Запрос.УстановитьПараметр("ГруппаОбучения", ГруппаОбучения);
		РезультатЗапроса = Запрос.Выполнить();				
		ПоследнийУрок = РезультатЗапроса.Выбрать();
		
		Если ПоследнийУрок.Количество() = 0 Тогда
			ИнформационнаяТЗ.Добавить().Описание = "Не найдено урока выбранной группы обучения: "+ГруппаОбучения;
		Иначе 
			Док = РезультатЗапроса.выгрузить()[0].Ссылка;
		КонецЕсли;  		
		
		Для Каждого Стр из Элементы.Календарь.ВыделенныеДаты Цикл 
			
			Запрос = Новый Запрос;
			Запрос.Текст = 
			"ВЫБРАТЬ
			|	Урок.Ссылка
			|ИЗ
			|	Документ.LM_Урок КАК Урок
			|ГДЕ
			|	Урок.Дата >= &НачалоДня
			|	И Урок.Дата <= &КонецДня
			|	И Урок.ГруппаОбучения = &ГруппаОбучения
			|	И Урок.Проведен = ИСТИНА"; 			
			Запрос.УстановитьПараметр("ГруппаОбучения", ГруппаОбучения);
			Запрос.УстановитьПараметр("КонецДня", КонецДня(Стр));
			Запрос.УстановитьПараметр("НачалоДня", НачалоДня(Стр));
			УрокиУжеСозданные = Запрос.Выполнить().Выгрузить(); 			
			Если УрокиУжеСозданные.Количество() > 0 Тогда
				НовСтр = ИнформационнаяТЗ.Добавить();
				НовСтр.Описание = "На "+Формат(Стр,"ДФ='dd.MM.yyyy ЧЧ:мм'")+" у "+ГруппаОбучения+" уже есть " +УрокиУжеСозданные[0].Ссылка +". Пропускаем...";
				НовСтр.Урок = УрокиУжеСозданные[0].Ссылка;
				Продолжить;
			КонецЕсли; 						
			
			НовДок = Документы.LM_Урок.СоздатьДокумент();
			
			ВремяЗанятия 	= ВремяНачала;
			КолЧасов 		= КоличествоЧасов;
			
			НовДок.Дата 			= Стр - ('00010101'-ВремяЗанятия);
			НовДок.ПредметОбучения 	= ПредметОбучения;
			НовДок.Педагог 			= Педагог;
			НовДок.Помещение 		= Помещение;
			НовДок.ГруппаОбучения 	= ГруппаОбучения;
			НовДок.КоличествоЧасов 	= КолЧасов;
			
			Для Каждого СтрУченик из Док.Ученики Цикл
				НоваяСтрока = НовДок.Ученики.Добавить();
				НоваяСтрока.Ученик 			= СтрУченик.Ученик;
				НоваяСтрока.Тариф			= СтрУченик.Тариф;
				НоваяСтрока.Скидка			= СтрУченик.Скидка;
				НоваяСтрока.СписатьОплату 	= СтрУченик.СписатьОплату;
			КонецЦикла;
			
			Попытка
				НовДок.Записать(РежимЗаписиДокумента.Проведение);
				НовСтр = ИнформационнаяТЗ.Добавить();
				НовСтр.Описание = "Проведен. Продление группы";
				НовСтр.Урок 	= НовДок.Ссылка;
			Исключение
				ИнформационнаяТЗ.Добавить().Описание = "Не удалось провести урок! " +ОписаниеОшибки();
			КонецПопытки;
			
		КонецЦикла;
				
	ИначеЕсли ПереводИзГруппы Тогда
		
		ИнформационнаяТЗ.Добавить().Описание = "--==НАЧАЛО ПереводИзГруппы " +ТекущаяДата();
		
		Для Каждого СтрДата из Элементы.Календарь.ВыделенныеДаты Цикл
			
			Для Каждого Уч из Ученики Цикл 
				//Ищем уроки выбранной группы по ученику
				//И удаляем ученика из уроков
				
				Если Не ЗначениеЗаполнено(Уч.Ученик) Тогда 
					Продолжить;
				КонецЕсли;
					
				Запрос = Новый Запрос;
				Запрос.Текст = 
				"ВЫБРАТЬ
				|	УрокУченики.Ссылка
				|ИЗ
				|	Документ.LM_Урок.Ученики КАК УрокУченики
				|ГДЕ
				|	УрокУченики.Ученик = &Ученик
				|	И УрокУченики.Ссылка.ПометкаУдаления = ЛОЖЬ
				|	И УрокУченики.Ссылка.ГруппаОбучения = &ГруппаОбучения
				|	И УрокУченики.Ссылка.Дата >= &Начало
				|	И УрокУченики.Ссылка.Дата <= &Окончание";
				
				Запрос.УстановитьПараметр("ГруппаОбучения", ИзГруппыОбучения);
				Запрос.УстановитьПараметр("Ученик", Уч.Ученик);
				Запрос.УстановитьПараметр("Окончание", КонецДня(СтрДата));
				Запрос.УстановитьПараметр("Начало", НачалоДня(СтрДата));
				
				РезультатЗапроса = Запрос.Выполнить();                  				
				ВыбУроки = РезультатЗапроса.Выбрать();				
				Пока ВыбУроки.Следующий() Цикл
					
					Ур = ВыбУроки.Ссылка.ПолучитьОбъект();
					        					      					
					Если Ур.Ученики.Количество() <= 1 Тогда
						Ур.УстановитьПометкуУдаления(Истина);
						НовСтр = ИнформационнаяТЗ.Добавить();
						НовСтр.Описание = "Удален урок. Перевод из группы ученика "+Уч.Ученик;
						НовСтр.Урок 	= ВыбУроки.Ссылка;
					Иначе
						с = Ур.Ученики.Индекс(Ур.Ученики.Найти(Уч.Ученик,"Ученик"));
						Ур.Ученики.Удалить(с);
						Попытка
							Ур.Записать(РежимЗаписиДокумента.Проведение);
							НовСтр = ИнформационнаяТЗ.Добавить();
							НовСтр.Описание = "Изменен урок. Перевод из группы ученика "+Уч.Ученик;
							НовСтр.Урок 	= ВыбУроки.Ссылка;
						Исключение
							ИнформационнаяТЗ.Добавить().Описание = "Не удалось провести урок! Перевод из группы ученика "+Уч.Ученик+" "+ОписаниеОшибки();
						КонецПопытки;
					КонецЕсли; 					       
										
				КонецЦикла;
			КонецЦикла;
		КонецЦикла;
		
			
			
		//Теперь создаем или добавляем учеников в занятия	
		Для Каждого Стр из Элементы.Календарь.ВыделенныеДаты Цикл		
			Запрос = Новый Запрос;
			Запрос.Текст = 
			"ВЫБРАТЬ
			|	Урок.Ссылка
			|ИЗ
			|	Документ.LM_Урок КАК Урок
			|ГДЕ
			|	Урок.Проведен = ИСТИНА
			|	И Урок.ГруппаОбучения = &ГруппаОбучения
			|	И Урок.Дата <= &ДатаОкончания
			|	И Урок.Дата >= &ДатаНачала";
			
			Запрос.УстановитьПараметр("ГруппаОбучения", ГруппаОбучения);
			Запрос.УстановитьПараметр("ДатаНачала", НачалоДня(Стр));
			Запрос.УстановитьПараметр("ДатаОкончания", КонецДня(Стр)); 				
			РезультатЗапроса = Запрос.Выполнить();				
			ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();
			
			Если ВыборкаДетальныеЗаписи.Количество() = 0 Тогда
				ДокС = Документы.LM_Урок.СоздатьДокумент();
				ДокС.Дата 			 = Стр-('00010101'-ВремяНачала);
				ДокС.ПредметОбучения = ПредметОбучения;
				ДокС.Педагог 		 = Педагог;
				ДокС.Помещение 		 = Помещение;
				ДокС.ГруппаОбучения  = ГруппаОбучения;
				ДокС.КоличествоЧасов = КоличествоЧасов;
				
				Для Каждого СтрУченик из Ученики Цикл
					Если Не ЗначениеЗаполнено(СтрУченик.Ученик) Тогда 
						Продолжить;
					КонецЕсли;
					НоваяСтрока = ДокС.Ученики.Добавить();
					НоваяСтрока.Ученик 			= СтрУченик.Ученик;
					НоваяСтрока.Тариф			= СтрУченик.Тариф;
					НоваяСтрока.Скидка			= СтрУченик.Скидка;
					НоваяСтрока.СписатьОплату 	= СтрУченик.СписатьОплату;
				КонецЦикла;
				
				Попытка
					//ДокС.Комментарий = ДокС.Комментарий+" СозданиеЗанятий (перевод). " +ТекущаяДата();
					ДокС.Записать(РежимЗаписиДокумента.Проведение);
					НовСтр = ИнформационнаяТЗ.Добавить();
					НовСтр.Описание = "Проведен (перевод)";
					НовСтр.Урок = ДокС.Ссылка;
				Исключение
					ИнформационнаяТЗ.Добавить().Описание = "Не удалось провести урок (перевод)! " +ОписаниеОшибки();
				КонецПопытки;
				
			КонецЕсли;
			
			Пока ВыборкаДетальныеЗаписи.Следующий() Цикл
				
				Док = ВыборкаДетальныеЗаписи.Ссылка.ПолучитьОбъект();
				
				ДокИзменен = Ложь;
				Для Каждого СтрУченик из Ученики Цикл
					Если Не ЗначениеЗаполнено(СтрУченик.Ученик) Тогда 
						Продолжить; 
					КонецЕсли;
					
					УченикУжеПрисутствует = Ложь;
					Для Каждого Уч из Док.Ученики Цикл
						Если СтрУченик.Ученик = Уч.Ученик Тогда
							НовСтр = ИнформационнаяТЗ.Добавить();
							НовСтр.Описание = "Ученик "+СтрУченик.Ученик+" уже присутствует в уроке! Пропускаем...";
							НовСтр.Урок = ВыборкаДетальныеЗаписи.Ссылка;
							УченикУжеПрисутствует = Истина;
						КонецЕсли; 							
					КонецЦикла;
					
					Если УченикУжеПрисутствует Тогда
						Продолжить;
					КонецЕсли;
					
					НоваяСтрока = Док.Ученики.Добавить();
					НоваяСтрока.Ученик 			= СтрУченик.Ученик;
					НоваяСтрока.Тариф			= СтрУченик.Тариф;
					НоваяСтрока.Скидка			= СтрУченик.Скидка;
					НоваяСтрока.СписатьОплату 	= СтрУченик.СписатьОплату;
					ДокИзменен = Истина;
				КонецЦикла;
				
				Если ДокИзменен Тогда
					Попытка
						Док.Записать(РежимЗаписиДокумента.Проведение);
						НовСтр = ИнформационнаяТЗ.Добавить();
						НовСтр.Описание = "Проведен урок! Добавление учеников (перевод)";
						НовСтр.Урок = Док.Ссылка;
					Исключение
						ИнформационнаяТЗ.Добавить().Описание = "Не удалось провести урок! Перевод. " +ОписаниеОшибки();
					КонецПопытки;
				КонецЕсли;  				
				
			КонецЦикла;	
			
		КонецЦикла;
		
	КонецЕсли; 	
	
КонецПроцедуры

&НаКлиенте
Процедура ВыполнитьДействие(Команда)
	
	Отказ = Ложь;
	
	ИнформационнаяТЗ.Очистить();
	
	Если Элементы.Календарь.ВыделенныеДаты.Количество() = 0 Тогда
		Сообщить("Не выбраны даты уроков!");
		Отказ = Истина;
	КонецЕсли;
	
	Если Элементы.Страницы.ТекущаяСтраница = Элементы.Страница1 Тогда
		Если Ученики.Количество() = 0 Тогда
			Сообщить("Не выбраны ученики!");
			Отказ = Истина;
		КонецЕсли;
	КонецЕсли;
			
	//Если ПереводИзГруппы и НЕ ЗначениеЗаполнено(ИзГруппыОбучения) Тогда
	//	Сообщить("Не выбрана Группа обучения из которой планируется перевод ученика(ов)!");
	//	Отказ = Истина;
	//КонецЕсли;
	
	//Если НЕ ДобавлениеВСуществующиеЗанятия и НЕ ПродлениеГруппы и НЕ ПереводИзГруппы Тогда
	//	Если ВремяНачала = '00010101' или КоличествоЧасов = '00010101' или НЕ ЗначениеЗаполнено(ПредметОбучения) Тогда 
	//		Сообщить("Не выбраны параметры создания уроков!");
	//		Отказ = Истина;
	//	КонецЕсли;
	//КонецЕсли; 
	
	Если Отказ Тогда
		Возврат;
	КонецЕсли;
	
	Состояние("Идет выполение...");
	ВыполнитьНаСервере();  	
	
	Оповестить("ЗакрытьФорму");
	Результат = Результат + "Выполнено!"+Символы.ПС;
	Состояние("Завершено!");
	
	Если ИнформационнаяТЗ.Количество()>0 Тогда
		Элементы.Страницы.ТекущаяСтраница  = Элементы.Страница5;
	КонецЕсли; 	
	
КонецПроцедуры

Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
	
	Если Найти(Метаданные.Имя,"LessonsManagement") = 0 Тогда
		Элементы.УченикиДобавить.Видимость = Ложь;
	КонецЕсли;
	
	НайтиДокументыНаСервере();

КонецПроцедуры

&НаКлиенте
Процедура ДобавлениеВСуществующиеЗанятияПриИзменении(Элемент)
	
	Если ЭтотОбъект.ДобавлениеВСуществующиеЗанятия Тогда
		ПродлениеГруппы		= Ложь;
		ПереводИзГруппы		= Ложь;
	КонецЕсли;
	
	ОбновитьВидимость();
	
	ГруппаОбученияПриИзмененииНаСервере(Ложь);
	
КонецПроцедуры

&НаКлиенте
Процедура ПродлениеГруппыПриИзменении(Элемент)
	
	Если ЭтотОбъект.ПродлениеГруппы Тогда
		ДобавлениеВСуществующиеЗанятия 	= Ложь;
		ПереводИзГруппы					= Ложь;
	КонецЕсли;
	
	ОбновитьВидимость();
	
	ГруппаОбученияПриИзмененииНаСервере(Истина);
	
КонецПроцедуры

&НаКлиенте
Процедура ПереводИзГруппыПриИзменении(Элемент)
	
	Если ЭтотОбъект.ПереводИзГруппы Тогда
		ДобавлениеВСуществующиеЗанятия 	= Ложь;
		ПродлениеГруппы					= Ложь;
	КонецЕсли;
	
	ОбновитьВидимость();
	
	ГруппаОбученияПриИзмененииНаСервере(Ложь);
	      	
КонецПроцедуры

&НаКлиенте
Процедура ГруппаОбученияПриИзменении(Элемент)
	
	УстановитьВремяВручную = Ложь;
	
	ГруппаОбученияПриИзмененииНаСервере(Ложь);
	
	ОбновитьВидимость();
	
КонецПроцедуры
Процедура ГруппаОбученияПриИзмененииНаСервере(СледМесяц)
	
	Элементы.Календарь.ВыделенныеДаты.Очистить();	
	
	Если ЗначениеЗаполнено(ЭтотОбъект.ГруппаОбучения) Тогда
		
		ЗаполнятьИзГруппыОбучения = Истина;
		
		Если ЭтотОбъект.ГруппаОбучения.ПН Тогда
			ДобавитьВСписок(1,"Календарь",СледМесяц);	
		КонецЕсли;
		Если ЭтотОбъект.ГруппаОбучения.ВТ Тогда
			ДобавитьВСписок(2,"Календарь",СледМесяц);	
		КонецЕсли;  
		Если ЭтотОбъект.ГруппаОбучения.СР Тогда
			ДобавитьВСписок(3,"Календарь",СледМесяц);	
		КонецЕсли; 
		Если ЭтотОбъект.ГруппаОбучения.ЧТ Тогда
			ДобавитьВСписок(4,"Календарь",СледМесяц);	
		КонецЕсли;
		Если ЭтотОбъект.ГруппаОбучения.ПТ Тогда
			ДобавитьВСписок(5,"Календарь",СледМесяц);	
		КонецЕсли;
		Если ЭтотОбъект.ГруппаОбучения.СБ Тогда
			ДобавитьВСписок(6,"Календарь",СледМесяц);	
		КонецЕсли;
		Если ЭтотОбъект.ГруппаОбучения.ВС Тогда
			ДобавитьВСписок(7,"Календарь",СледМесяц);	
		КонецЕсли;
		
		Если ДобавлениеВСуществующиеЗанятия Тогда
			
			Запрос = Новый Запрос;
			Запрос.Текст = 
			"ВЫБРАТЬ
			|	ФизЛицаГруппыОбучения.Ссылка КАК Ссылка
			|ИЗ
			|	Справочник.LM_ФизЛица.ГруппыОбучения КАК ФизЛицаГруппыОбучения
			|ГДЕ
			|	ФизЛицаГруппыОбучения.Ссылка.ТолькоВыбранныеГруппыОбучения
			|	И ФизЛицаГруппыОбучения.ГруппаОбучения = &ГруппаОбучения";	
			Запрос.УстановитьПараметр("ГруппаОбучения", ГруппаОбучения);	
			РезультатЗапроса = Запрос.Выполнить(); 	
			ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();
			
			Пока ВыборкаДетальныеЗаписи.Следующий() Цикл
				НовУч = Ученики.Добавить();
				НовУч.Ученик = ВыборкаДетальныеЗаписи.Ссылка;
			КонецЦикла;
			
		КонецЕсли;
		
		Педагог 		= ЭтотОбъект.ГруппаОбучения.Педагог;
		ПредметОбучения = ЭтотОбъект.ГруппаОбучения.ПредметОбучения;
		ВремяНачала 	= ЭтотОбъект.ГруппаОбучения.Время;
		КоличествоЧасов = ЭтотОбъект.ГруппаОбучения.Продолжительность;
		Помещение 		= ЭтотОбъект.ГруппаОбучения.Помещение;
		Тариф 			= ЭтотОбъект.ГруппаОбучения.Тариф;
		
	Иначе
		
		ЗаполнятьИзГруппыОбучения = Ложь;
		
	КонецЕсли; 	
	
	Если ЗначениеЗаполнено(ГруппаОбучения) и ПродлениеГруппы Тогда
		Запрос = Новый Запрос;
		Запрос.Текст = 
		"ВЫБРАТЬ ПЕРВЫЕ 1
		|	Урок.Ссылка,
		|	Урок.Дата КАК Дата
		|ИЗ
		|	Документ.LM_Урок КАК Урок
		|ГДЕ
		|	Урок.Проведен = ИСТИНА
		|	И Урок.ГруппаОбучения = &ГруппаОбучения
		|
		|УПОРЯДОЧИТЬ ПО
		|	Дата УБЫВ
		|АВТОУПОРЯДОЧИВАНИЕ";
		Запрос.УстановитьПараметр("ГруппаОбучения", ГруппаОбучения);
		РезультатЗапроса = Запрос.Выполнить();				
		ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();
		
		Ученики.Очистить();		
		Пока ВыборкаДетальныеЗаписи.Следующий() Цикл
			Для Каждого Стр из ВыборкаДетальныеЗаписи.Ссылка.Ученики Цикл
				НовСтрУч = Ученики.Добавить();
				НовСтрУч.Ученик = Стр.Ученик;
				НовСтрУч.Тариф 	= Стр.Тариф;
			КонецЦикла;			
		КонецЦикла;  		
	КонецЕсли; 	
	
КонецПроцедуры

Процедура ДобавитьВСписок(ДеньНедели, Календ, СледМесяц) 	
	
	Если СледМесяц Тогда
		ДатаНач 	= КонецМесяца(ТекущаяДата())+1;
	Иначе
		ДатаНач 	= ТекущаяДата();
	КонецЕсли;
	
	ДатаКонец 	= КонецМесяца(ДатаНач); 
	Пока ДатаНач <= ДатаКонец Цикл
		Если ДеньНедели(ДатаНач) = ДеньНедели Тогда
			Элементы[Календ].ВыделенныеДаты.Добавить(НачалоДня(ДатаНач));
		КонецЕсли;
		ДатаНач = ДатаНач +86400;
	КонецЦикла;
	
КонецПроцедуры

&НаКлиенте
Процедура ОбновитьВидимость()
	
	Если ПереводИзГруппы Тогда 
		Элементы.ИзГруппыОбучения.Видимость = Истина;
	Иначе
		Элементы.ИзГруппыОбучения.Видимость = Ложь;
	КонецЕсли;
	
	Элементы.ВремяНачала.Доступность 		= Истина;
	Элементы.КоличествоЧасов.Доступность 	= Истина;
	
	ВремяНачала = Неопределено;
	КоличествоЧасов = Неопределено;
	
	Если ЗаполнятьИзГруппыОбучения Тогда 
		Элементы.Помещение.Доступность 			= Ложь;
		Элементы.Педагог.Доступность 			= Ложь;
		Элементы.ПредметОбучения.Доступность 	= Ложь;
		Элементы.ВремяНачала.Видимость 			= Ложь;
		Элементы.КоличествоЧасов.Видимость 		= Ложь;
		Элементы.Тариф.Доступность 				= Ложь;
	Иначе
		Элементы.Помещение.Доступность 			= Истина;
		Элементы.Педагог.Доступность 			= Истина;
		Элементы.ПредметОбучения.Доступность 	= Истина;
		Элементы.Тариф.Доступность 				= Истина;
	КонецЕсли;
	
	Если НЕ УстановитьВремяВручную Тогда
		Элементы.ВремяНачала.Видимость 		= Ложь;
		Элементы.КоличествоЧасов.Видимость 	= Ложь;
	Иначе
		Элементы.ВремяНачала.Видимость 		= Истина;
		Элементы.КоличествоЧасов.Видимость 	= Истина;
	КонецЕсли;
	
	ОбновитьВидимостьНаСервере();
		
КонецПроцедуры

Процедура ОбновитьВидимостьНаСервере()
	
	Если ЗаполнятьИзГруппыОбучения Тогда 
		
		Если УстановитьВремяВручную Тогда
			ВремяНачала 	= ГруппаОбучения.Время;
			КоличествоЧасов = ГруппаОбучения.Продолжительность;
		КонецЕсли;
		
		Педагог			= ГруппаОбучения.Педагог;
		Помещение		= ГруппаОбучения.Помещение;
		ПредметОбучения	= ГруппаОбучения.ПредметОбучения;
		Тариф			= ГруппаОбучения.Тариф;
		
	КонецЕсли;
	
	Если НЕ Тариф.Пустая() Тогда
		
		Запрос = Новый Запрос;
		Запрос.Текст = 
		"ВЫБРАТЬ ПЕРВЫЕ 1
		|	LM_ЦеныТарифовСрезПоследних.Период КАК Период,
		|	LM_ЦеныТарифовСрезПоследних.КоличествоЧасов КАК КоличествоЧасов,
		|	LM_ЦеныТарифовСрезПоследних.КоличествоУроков КАК КоличествоУроков,
		|	LM_ЦеныТарифовСрезПоследних.Сумма КАК Сумма
		|ИЗ
		|	РегистрСведений.LM_ЦеныТарифов.СрезПоследних(&ТекДата, ) КАК LM_ЦеныТарифовСрезПоследних
		|ГДЕ
		|	LM_ЦеныТарифовСрезПоследних.Тариф = &Тариф
		|
		|УПОРЯДОЧИТЬ ПО
		|	Период УБЫВ";
		Запрос.УстановитьПараметр("Тариф", Тариф);
		Запрос.УстановитьПараметр("ТекДата", ТекущаяДата());
		Цены = Запрос.Выполнить().Выгрузить();
		
		Если Цены.Количество() > 0 Тогда
			Если Цены[0].КоличествоЧасов > 0 Тогда
				Элементы.Декорация3.Заголовок = "" +Формат(Цены[0].Сумма/Цены[0].КоличествоЧасов,"ЧДЦ=2")+ " за 1 час ("
				+Формат(Цены[0].Сумма,"ЧДЦ=2")+ " / " +Цены[0].КоличествоЧасов+ " ч.)";				
			ИначеЕсли Цены[0].КоличествоУроков > 0 Тогда
				Элементы.Декорация3.Заголовок = "" +Формат(Цены[0].Сумма/Цены[0].КоличествоУроков,"ЧДЦ=2")+ " за 1 урок ("
				+Формат(Цены[0].Сумма,"ЧДЦ=2")+ " / " +Цены[0].КоличествоУроков+ " ур.)";
			КонецЕсли;
		Иначе
			Элементы.Декорация3.Заголовок = "Нет действующих цен! Создайте новую цену в тарифе!";
		КонецЕсли;
		
	Иначе		
		//Элементы.Декорация3.Заголовок = "Тариф не выбран: - цены не рассчитаны!"; 		
	КонецЕсли;

КонецПроцедуры        

&НаКлиенте
Процедура ПриОткрытии(Отказ)
	
	ГруппаОбученияПриИзмененииНаСервере(Ложь);
	
	ОбновитьВидимость();
	
КонецПроцедуры

&НаКлиенте
Процедура ИзГруппыОбученияПриИзменении(Элемент)
	ИзГруппыОбученияПриИзмененииНаСервере(Ложь);
КонецПроцедуры
Процедура ИзГруппыОбученияПриИзмененииНаСервере(СледМесяц)
	
	Элементы.Календарь.ВыделенныеДаты.Очистить();
	
	Если ЗначениеЗаполнено(ЭтотОбъект.ИзГруппыОбучения) Тогда
		Если ЭтотОбъект.ИзГруппыОбучения.ПН Тогда
			ДобавитьВСписок(1,"Календарь",СледМесяц);	
		КонецЕсли;
		Если ЭтотОбъект.ИзГруппыОбучения.ВТ Тогда
			ДобавитьВСписок(2,"Календарь",СледМесяц);	
		КонецЕсли;  
		Если ЭтотОбъект.ИзГруппыОбучения.СР Тогда
			ДобавитьВСписок(3,"Календарь",СледМесяц);	
		КонецЕсли; 
		Если ЭтотОбъект.ИзГруппыОбучения.ЧТ Тогда
			ДобавитьВСписок(4,"Календарь",СледМесяц);	
		КонецЕсли;
		Если ЭтотОбъект.ИзГруппыОбучения.ПТ Тогда
			ДобавитьВСписок(5,"Календарь",СледМесяц);	
		КонецЕсли;
		Если ЭтотОбъект.ИзГруппыОбучения.СБ Тогда
			ДобавитьВСписок(6,"Календарь",СледМесяц);	
		КонецЕсли;
		Если ЭтотОбъект.ИзГруппыОбучения.ВС Тогда
			ДобавитьВСписок(7,"Календарь",СледМесяц);	
		КонецЕсли; 
	КонецЕсли;
	
КонецПроцедуры

&НаКлиенте
Процедура УченикиУченикСоздание(Элемент, СтандартнаяОбработка)
	
	СтандартнаяОбработка = Ложь;
	
	ПараметрыСтроки = Новый Структура;
	
	Назв = СокрЛП(Элемент.ТекстРедактирования);
	
	Если Найти(Назв," ") > 0 Тогда
		Симв1 = Найти(Назв," ");
		ПараметрыСтроки.Вставить("Наименование",Лев(Назв,Симв1-1));
		Назв = СокрЛП(Сред(Назв,Симв1+1));
	Иначе
		ПараметрыСтроки.Вставить("Наименование",Назв);
		Назв = "";
	КонецЕсли;
	
	ПараметрыСтроки.Вставить("Группа","Ученики");
	
	Пар = Новый Структура("Ключ2", ПараметрыСтроки);
	
	ОткрытьФорму("Справочник.LM_ФизЛица.Форма.ФормаЭлемента",Пар,ЭтотОбъект,УникальныйИдентификатор,ВариантОткрытияОкна.ОтдельноеОкно,,,РежимОткрытияОкнаФормы.БлокироватьОкноВладельца);

КонецПроцедуры

&НаКлиенте
Процедура Очистить(Команда)
	
	ИзГруппыОбучения 				= Неопределено;
	ГруппаОбучения   				= Неопределено;
	ДобавлениеВСуществующиеЗанятия 	= Истина;
	ПереводИзГруппы				 	= Ложь;
	ПродлениеГруппы				 	= Ложь;
	Помещение						= Неопределено;
	Педагог							= Неопределено;
	ПредметОбучения					= Неопределено;
	ВремяНачала						= '00010101';
	КоличествоЧасов					= '00010101';
	ЗаполнятьИзГруппыОбучения		= Ложь;
	УстановитьВремяВручную			= Истина;
	СтатусУрока						= Неопределено;
	
	Результат = "";
	Ученики.Очистить();
	ИнформационнаяТЗ.Очистить();
	Элементы.Календарь.ВыделенныеДаты.Очистить();
	
	ОбновитьВидимость();
	
КонецПроцедуры

&НаКлиенте
Процедура СписатьОплаты(Команда) 	
	Для Каждого Стр из Ученики Цикл
		Стр.СписатьОплату = Истина;
	КонецЦикла;	
КонецПроцедуры
&НаКлиенте
Процедура УбратьСписатьОплаты(Команда) 	
	Для Каждого Стр из Ученики Цикл
		Стр.СписатьОплату = Ложь;
	КонецЦикла; 	
КонецПроцедуры

Функция ВернутьПапкуУченики()
	Возврат Справочники.LM_ФизЛица.Ученики.Ссылка;
КонецФункции

&НаКлиенте
Процедура ПодборУчениковЗавершение(Результат,Параметры) Экспорт 
	Если Результат <> Неопределено Тогда
		Для Каждого Ученик Из Результат Цикл
			НоваяСтрока = Ученики.Добавить();
			НоваяСтрока.Ученик = Ученик;
			НоваяСтрока.Скидка = ПолучитьСкидкуУченика(Ученик);
		КонецЦикла;
	КонецЕсли;
КонецПроцедуры

&НаКлиенте
Процедура ПодборУчеников(Команда)
	ОП = Новый ОписаниеОповещения("ПодборУчениковЗавершение",ЭтотОбъект);
	ПП = Новый Структура("МножественныйВыбор",Истина);  
	Отбор = Новый Структура("Родитель",ВернутьПапкуУченики());
	ПП.Вставить("Отбор", Отбор);
	ОткрытьФорму("Справочник.LM_ФизЛица.Форма.ФормаВыбора",ПП,ЭтотОбъект,,,,ОП,РежимОткрытияОкнаФормы.БлокироватьОкноВладельца);
КонецПроцедуры

Процедура НайтиДокументыНаСервере()
	
	МассивУроков = Новый Массив;
	
	Для Каждого Стр из Элементы.Календарь.ВыделенныеДаты Цикл
		
		Запрос = Новый Запрос;
		Запрос.Текст = 
		"ВЫБРАТЬ
		|	Урок.Ссылка КАК Ссылка
		|ИЗ
		|	Документ.LM_Урок КАК Урок
		|ГДЕ
		|	Урок.Проведен = ИСТИНА
		|	И Урок.Окончание <= &ДатаОкончания
		|	И Урок.Дата >= &ДатаНачала
		//|	И Урок.Педагог = &Педагог
		|	И Урок.ПредметОбучения = &ПредметОбучения
		|	И Урок.Помещение = &Помещение";			
		
		Если ЗаполнятьИзГруппыОбучения Тогда
			СтруктураВременИзГруппы = ПолучитьВремяИзГруппы(Стр);
			Если СтруктураВременИзГруппы = Неопределено Тогда
				Продолжить;
			КонецЕсли;
			
			Запрос.УстановитьПараметр("ДатаНачала", Стр-('00010101'-СтруктураВременИзГруппы.ВремяНачала)); 
			Запрос.УстановитьПараметр("ДатаОкончания", Стр-('00010101'-СтруктураВременИзГруппы.ВремяОкончания));
		Иначе
			Запрос.УстановитьПараметр("ДатаНачала", Стр-('00010101'-ВремяНачала)); 
			Запрос.УстановитьПараметр("ДатаОкончания", Стр-('00010101'-ВремяНачала)-('00010101'-КоличествоЧасов));
		КонецЕсли;
		
		Запрос.УстановитьПараметр("ПредметОбучения", ПредметОбучения);
		//Запрос.УстановитьПараметр("Педагог", Педагог);
		Запрос.УстановитьПараметр("Помещение", Помещение);
		
		РезультатЗапроса = Запрос.Выполнить();				
		ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();
		
		Пока ВыборкаДетальныеЗаписи.Следующий() Цикл
			МассивУроков.Добавить(ВыборкаДетальныеЗаписи.Ссылка);
		КонецЦикла;				
		
	КонецЦикла;
	
	Урок = Элементы.НайденныеДокументы2.ТекущаяСтрока;
	НайденныеДокументы2.Отбор.Элементы.Очистить();
	ЭлементОтбора = НайденныеДокументы2.Отбор.Элементы.Добавить(Тип("ЭлементОтбораКомпоновкиДанных"));
	ЭлементОтбора.ЛевоеЗначение = Новый ПолеКомпоновкиДанных("Ссылка");
	ЭлементОтбора.ВидСравнения = ВидСравненияКомпоновкиДанных.ВСписке;
	ЭлементОтбора.ПравоеЗначение = МассивУроков;
	ЭлементОтбора = НайденныеДокументы2.Отбор.Элементы[0];
	ЭлементОтбора.Использование = Истина;
	Элементы.НайденныеДокументы2.Обновить();
	
КонецПроцедуры

&НаКлиенте
Процедура НайтиДокументы(Команда) 	
	НайтиДокументыНаСервере(); 	
КонецПроцедуры

Функция ПолучитьВремяИзГруппыОбучения(Стр)	
	
	ВремяЗанятия = ВремяНачала;
	
	ДеньНедели = Формат(Стр,"ДФ=ддд");
	Если ДеньНедели = "Пн" Тогда
		ВремяЗанятия = ?(ГруппаОбучения.ПН,ГруппаОбучения.ПНВремя,ВремяЗанятия);
	ИначеЕсли ДеньНедели = "Вт" Тогда
		ВремяЗанятия = ?(ГруппаОбучения.ВТ,ГруппаОбучения.ВТВремя,ВремяЗанятия);
	ИначеЕсли ДеньНедели = "Ср" Тогда
		ВремяЗанятия = ?(ГруппаОбучения.СР,ГруппаОбучения.СРВремя,ВремяЗанятия);
	ИначеЕсли ДеньНедели = "Чт" Тогда
		ВремяЗанятия = ?(ГруппаОбучения.ЧТ,ГруппаОбучения.ЧТВремя,ВремяЗанятия);
	ИначеЕсли ДеньНедели = "Пт" Тогда
		ВремяЗанятия = ?(ГруппаОбучения.ПТ,ГруппаОбучения.ПТВремя,ВремяЗанятия);
	ИначеЕсли ДеньНедели = "Сб" Тогда
		ВремяЗанятия = ?(ГруппаОбучения.СБ,ГруппаОбучения.СБВремя,ВремяЗанятия);
	ИначеЕсли ДеньНедели = "Вс" Тогда
		ВремяЗанятия = ?(ГруппаОбучения.ВС,ГруппаОбучения.ВСВремя,ВремяЗанятия);
	КонецЕсли;
	
	Возврат ВремяЗанятия;
	
КонецФункции

&НаКлиенте
Процедура ЗаполнятьИзГруппыОбученияПриИзменении(Элемент)
	
	Если ЗаполнятьИзГруппыОбучения Тогда
		Элементы.ВремяБратьИзГруппы.Доступность = Истина;
		УстановитьВремяВручную 					= Ложь;
		Элементы.ВремяНачала.Видимость 			= Ложь;
		Элементы.КоличествоЧасов.Видимость 		= Ложь;
	Иначе
		Элементы.ВремяБратьИзГруппы.Доступность = Ложь;
		УстановитьВремяВручную 					= Истина;
		Элементы.ВремяНачала.Видимость 			= Истина;
		Элементы.КоличествоЧасов.Видимость 		= Истина;
	КонецЕсли;
	
	ОбновитьВидимость();
	
КонецПроцедуры

&НаКлиенте
Процедура ВремяБратьИзГруппыПриИзменении(Элемент)
	
	Если НЕ УстановитьВремяВручную и ЗначениеЗаполнено(ГруппаОбучения) Тогда
		Элементы.ВремяНачала.Видимость 		= Ложь;
		Элементы.КоличествоЧасов.Видимость 	= Ложь;
	Иначе
		Элементы.ВремяНачала.Видимость 		= Истина;
		Элементы.КоличествоЧасов.Видимость 	= Истина;
	КонецЕсли;
	
	ВремяНачала = Неопределено;
	КоличествоЧасов = Неопределено;

КонецПроцедуры

&НаКлиенте
Процедура СтраницыПриСменеСтраницы(Элемент, ТекущаяСтраница)
	Если Элементы.Страницы.ТекущаяСтраница = Элементы.Страница4 Тогда
		НайтиДокументыНаСервере();
	КонецЕсли;
КонецПроцедуры

&НаКлиенте
Процедура ЗаполнитьСледующийМесяц(Команда)
	ГруппаОбученияПриИзмененииНаСервере(Истина);
КонецПроцедуры

&НаКлиенте
Процедура ЗаполнитьЭтотМесяц(Команда)
	ГруппаОбученияПриИзмененииНаСервере(Ложь);
КонецПроцедуры

&НаКлиенте
Процедура УченикиУченикПриИзменении(Элемент) 	
	ТекДанные = Элементы.Ученики.ТекущиеДанные;
	ТекДанные.Скидка 	= ПолучитьСкидкуУченика(ТекДанные.Ученик);
	ТекДанные.Тариф 	= ПолучитьТарифУченика(ТекДанные.Ученик);
КонецПроцедуры 
Функция ПолучитьСкидкуУченика(Ученик)
	Возврат Ученик.Скидка;
КонецФункции
Функция ПолучитьТарифУченика(Ученик)
	Возврат Ученик.Тариф;
КонецФункции

&НаКлиенте
Процедура ТарифПриИзменении(Элемент)
	
	Для Каждого Стр из Ученики Цикл
		Стр.Тариф = Тариф;
	КонецЦикла;
	
	ОбновитьВидимость();
	
КонецПроцедуры

