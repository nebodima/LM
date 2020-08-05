﻿
Процедура ВыполнитьНаСервере()
	
	Если ДобавлениеВСуществующиеЗанятия Тогда
		
		ИнформационнаяТЗ.Добавить().Описание = "--==НАЧАЛО СозданиеИлиДобавлениеВСуществующиеЗанятия " +ТекущаяДата();
		  
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
				|	И Урок.Педагог = &Педагог
				|	И Урок.ПредметОбучения = &ПредметОбучения
				//|	И Урок.Помещение = &Помещение
				|	И Урок.Дата >= &ДатаНачала";
				
				Запрос.УстановитьПараметр("ДатаНачала", Стр-('00010101'-ВремяНачала)); 
				Запрос.УстановитьПараметр("ДатаОкончания", Стр-('00010101'-ВремяНачала)-('00010101'-КоличествоЧасов));
				
				Если ЗаполнятьИзГруппыОбучения Тогда
					//Запрос.УстановитьПараметр("ГруппаОбучения", ГруппаОбучения);
					Запрос.УстановитьПараметр("ПредметОбучения", ГруппаОбучения.ПредметОбучения);
					Запрос.УстановитьПараметр("Педагог", ГруппаОбучения.Педагог);
					//Запрос.УстановитьПараметр("Помещение", ГруппаОбучения.Помещение);
					Запрос.УстановитьПараметр("ДатаНачала", Стр-('00010101'-ГруппаОбучения.ВремяНачала)); 
					Запрос.УстановитьПараметр("ДатаОкончания", Стр-('00010101'-ГруппаОбучения.ВремяНачала)-('00010101'-ГруппаОбучения.Продолжительность));
				Иначе
					//Запрос.УстановитьПараметр("ГруппаОбучения", ГруппаОбучения);
					Запрос.УстановитьПараметр("ПредметОбучения", ПредметОбучения);
					Запрос.УстановитьПараметр("Педагог", Педагог);
					//Запрос.УстановитьПараметр("Помещение", Помещение);
				КонецЕсли;				
				
				РезультатЗапроса = Запрос.Выполнить();				
				ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();
				
				Если ВыборкаДетальныеЗаписи.Количество() = 0 Тогда
					ДокС = Документы.LM_Урок.СоздатьДокумент();
					
					ВремяЗанятия 	= ВремяНачала;
					КолЧасов 		= КоличествоЧасов;
					
					//ДокС.Организация	 = Справочники.Организации.ПолучитьОрганизациюПоУмолчанию();
					ДокС.Дата 			 = Стр-('00010101'-ВремяЗанятия);
					ДокС.ПредметОбучения = ПредметОбучения;
					ДокС.Педагог 		 = Педагог;
					ДокС.Помещение 		 = Помещение;
					ДокС.ГруппаОбучения  = ГруппаОбучения;
					ДокС.КоличествоЧасов = КолЧасов;
					
					Для Каждого СтрУченик из Ученики Цикл
						Если Не ЗначениеЗаполнено(СтрУченик.Ученик) Тогда 
							Продолжить;
						КонецЕсли;
						НоваяСтрока = ДокС.Ученики.Добавить();
						НоваяСтрока.Ученик 			= СтрУченик.Ученик;
						НоваяСтрока.Тариф			= СтрУченик.Тариф;
						НоваяСтрока.Коэффициент		= СтрУченик.Скидка;
						НоваяСтрока.СписатьОплату 	= СтрУченик.СписатьОплату;
					КонецЦикла;
					
					Попытка
						ДокС.Записать(РежимЗаписиДокумента.Проведение);
						НовСтр = ИнформационнаяТЗ.Добавить();
						НовСтр.Урок = ДокС.Ссылка;
						НовСтр.Описание = "Проведен";
					Исключение
						ИнформационнаяТЗ.Добавить().Описание = "Не удалось провести урок!";
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
								НовСтр.Описание = "Ученик "+СтрУченик.Ученик+" уже присутствует в уроке № " +Док.Номер+
								" от " +Формат(Док.Дата,"ДФ=dd.MM.yyyy")+ " с " +Формат(Док.Дата,"ДФ=HH:mm")+ " по " +Формат(Док.Окончание,"ДФ=HH:mm")+ ". Пропускаем...";
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
						НоваяСтрока.Коэффициент		= СтрУченик.Скидка;
						НоваяСтрока.СписатьОплату 	= СтрУченик.СписатьОплату;
						
						ДокИзменен = Истина;
						
					КонецЦикла;
					
					Если ДокИзменен Тогда
						Попытка
							Док.Записать(РежимЗаписиДокумента.Проведение);
							НовСтр = ИнформационнаяТЗ.Добавить();
							НовСтр.Описание = "Проведен. Добавление учеников";
							НовСтр.Урок 	= Док.Ссылка;
						Исключение
							ИнформационнаяТЗ.Добавить().Описание = "Не удалось провести урок! " +ОписаниеОшибки();
						КонецПопытки;
					КонецЕсли;  				
					
				КонецЦикла;
				
			//Иначе //группа обучения не выбрана
			//	
			//	Запрос = Новый Запрос;
			//	Запрос.Текст = 
			//	"ВЫБРАТЬ ПЕРВЫЕ 1
			//	|	Урок.Ссылка
			//	|ИЗ
			//	|	Документ.Урок КАК Урок
			//	|ГДЕ
			//	|	Урок.Проведен = ИСТИНА
			//	|	И Урок.Окончание <= &ДатаОкончания
			//	|	И Урок.Дата >= &ДатаНачала
			//	|	И Урок.ПредметОбучения = &ПредметОбучения
			//	|	И Урок.Педагог = &Педагог
			//	|	И Урок.Помещение = &Помещение";
			//	
			//	Запрос.УстановитьПараметр("ПредметОбучения", ПредметОбучения);
			//	Запрос.УстановитьПараметр("Педагог", Педагог);
			//	Запрос.УстановитьПараметр("Помещение", Помещение);
			//	Запрос.УстановитьПараметр("ДатаНачала", Стр-('00010101'-ВремяНачала)); 
			//	Запрос.УстановитьПараметр("ДатаОкончания", Стр-('00010101'-ВремяНачала)-('00010101'-КоличествоЧасов));
			//	
			//	РезультатЗапроса = Запрос.Выполнить();				
			//	ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();
			//	
			//	Если ВыборкаДетальныеЗаписи.Количество() = 0 Тогда
			//		ДокС = Документы.Урок.СоздатьДокумент();
			//		ДокС.Дата 			 = Стр - ('00010101' - ВремяНачала);
			//		ДокС.ПредметОбучения = ПредметОбучения;
			//		ДокС.Педагог 		 = Педагог;
			//		ДокС.Помещение 		 = Помещение;
			//		ДокС.КоличествоЧасов = КоличествоЧасов;
			//		
			//		Для Каждого СтрУченик из Ученики Цикл
			//			Если Не ЗначениеЗаполнено(СтрУченик.Ученик) Тогда 
			//				Продолжить;
			//			КонецЕсли;
			//			НоваяСтрока = ДокС.Ученики.Добавить();
			//			НоваяСтрока.Ученик 			= СтрУченик.Ученик;
			//			НоваяСтрока.Тариф			= СтрУченик.Тариф;
			//			НоваяСтрока.Коэффициент		= СтрУченик.Скидка;
			//			НоваяСтрока.СписатьОплату 	= СтрУченик.СписатьОплату;
			//		КонецЦикла;
			//		
			//		Попытка
			//			ДокС.Записать(РежимЗаписиДокумента.Проведение);
			//			НовСтр = ИнформационнаяТЗ.Добавить();
			//			НовСтр.Описание = "Проведен";
			//			НовСтр.Урок 	= ДокС.Ссылка; 
			//		Исключение
			//			ИнформационнаяТЗ.Добавить().Описание = "Не удалось провести урок! " +ОписаниеОшибки();
			//		КонецПопытки;
			//		
			//	КонецЕсли;
			//	
			//	Пока ВыборкаДетальныеЗаписи.Следующий() Цикл
			//		
			//		Док = ВыборкаДетальныеЗаписи.Ссылка.ПолучитьОбъект();
			//		
			//		ДокИзменен = Ложь;
			//		
			//		Для Каждого СтрУченик из Ученики Цикл
			//			
			//			Если Не ЗначениеЗаполнено(СтрУченик.Ученик) Тогда 
			//				Продолжить; 
			//			КонецЕсли;
			//			
			//			УченикУжеПрисутствует = Ложь;
			//			Для Каждого Уч из Док.Ученики Цикл
			//				Если СтрУченик.Ученик = Уч.Ученик Тогда
			//					НовСтр = ИнформационнаяТЗ.Добавить();
			//					НовСтр.Описание = "Ученик "+СтрУченик.Ученик+" уже присутствует в уроке № " +Док.Номер+
			//					" от " +Формат(Док.Дата,"ДФ=dd.MM.yyyy")+ " с " +Формат(Док.Дата,"ДФ=HH:mm")+ " по " +Формат(Док.Окончание,"ДФ=HH:mm")+ ". Пропускаем...";
			//					НовСтр.Урок = ВыборкаДетальныеЗаписи.Ссылка; 
			//					УченикУжеПрисутствует = Истина;
			//				КонецЕсли; 							
			//			КонецЦикла;
			//			
			//			Если УченикУжеПрисутствует Тогда
			//				Продолжить;
			//			КонецЕсли;
			//			
			//			НоваяСтрока = Док.Ученики.Добавить();
			//			НоваяСтрока.Ученик 			= СтрУченик.Ученик;
			//			НоваяСтрока.Тариф			= СтрУченик.Тариф;
			//			НоваяСтрока.Коэффициент		= СтрУченик.Скидка;
			//			НоваяСтрока.СписатьОплату 	= СтрУченик.СписатьОплату;
			//			ДокИзменен = Истина;
			//			
			//		КонецЦикла;
			//		
			//		Если ДокИзменен Тогда
			//			Попытка
			//				Док.Записать(РежимЗаписиДокумента.Проведение);
			//				НовСтр = ИнформационнаяТЗ.Добавить();
			//				НовСтр.Описание = "Проведен. Добавление учеников";
			//				НовСтр.Урок 	= Док.Ссылка;
			//			Исключение
			//				ИнформационнаяТЗ.Добавить().Описание = "Не удалось провести урок! " +ОписаниеОшибки();
			//			КонецПопытки;
			//		КонецЕсли;
			//		
			//	КонецЦикла;
			//	
			//КонецЕсли;
			
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
				НоваяСтрока.Коэффициент		= СтрУченик.Скидка;
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
					НоваяСтрока.Коэффициент		= СтрУченик.Скидка;
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
					НоваяСтрока.Коэффициент		= СтрУченик.Скидка;
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
	
	Если НЕ ДобавлениеВСуществующиеЗанятия и НЕ ПродлениеГруппы и НЕ ПереводИзГруппы Тогда
		Сообщить("Не выбрано ни одно действие с уроками! Поставьте галочку.");
		Отказ = Истина;
	КонецЕсли; 		
	
	Элементы.ИнформационнаяТЗ.Видимость = Истина;	
	ИнформационнаяТЗ.Очистить();
	
	
	
	Если Элементы.Календарь.ВыделенныеДаты.Количество() = 0 Тогда
		Сообщить("Не выбраны даты уроков!");
		Отказ = Истина;
	КонецЕсли;
	
	Если ДобавлениеВСуществующиеЗанятия Тогда
		Если Ученики.Количество() = 0 Тогда
			Сообщить("Не выбраны ученики!");
			Отказ = Истина;
		КонецЕсли;
	КонецЕсли;
			
	Если ПереводИзГруппы и НЕ ЗначениеЗаполнено(ИзГруппыОбучения) Тогда
		Сообщить("Не выбрана Группа обучения из которой планируется перевод ученика(ов)!");
		Отказ = Истина;
	КонецЕсли;
	
	Если НЕ ДобавлениеВСуществующиеЗанятия и НЕ ПродлениеГруппы и НЕ ПереводИзГруппы Тогда
		Если ВремяНачала = '00010101' или КоличествоЧасов = '00010101' или НЕ ЗначениеЗаполнено(ПредметОбучения) Тогда 
			Сообщить("Не выбраны параметры создания уроков!");
			Отказ = Истина;
		КонецЕсли;
	КонецЕсли; 
	
	Если НЕ ЗначениеЗаполнено(ВремяНачала) Тогда
		Сообщить("Не указано время начала урока(ов)!");
		Отказ = Истина;
	КонецЕсли;      
	
	Если Отказ Тогда
		Возврат;
	КонецЕсли;
	
	ВыполнитьНаСервере();
	
	Оповестить("ЗакрытьФорму");
	Результат = Результат + "Выполнено!"+Символы.ПС;
	
КонецПроцедуры

Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
	ДобавлениеВСуществующиеЗанятия 	= Истина;
КонецПроцедуры

&НаКлиенте
Процедура ДобавлениеВСуществующиеЗанятияПриИзменении(Элемент)
	
	Если ЭтотОбъект.ДобавлениеВСуществующиеЗанятия Тогда
		ПродлениеГруппы		= Ложь;
		ПереводИзГруппы		= Ложь;
	КонецЕсли;
	
	ОбновитьВидимость();
	
	ГруппаОбученияПриИзмененииНаСервере();
	
КонецПроцедуры

&НаКлиенте
Процедура ПродлениеГруппыПриИзменении(Элемент)
	
	Если ЭтотОбъект.ПродлениеГруппы Тогда
		ДобавлениеВСуществующиеЗанятия 	= Ложь;
		ПереводИзГруппы					= Ложь;
	КонецЕсли;
	
	ОбновитьВидимость();
	
	ГруппаОбученияПриИзмененииНаСервере();
	
КонецПроцедуры

&НаКлиенте
Процедура ПереводИзГруппыПриИзменении(Элемент)
	
	Если ЭтотОбъект.ПереводИзГруппы Тогда
		ДобавлениеВСуществующиеЗанятия 	= Ложь;
		ПродлениеГруппы					= Ложь;
	КонецЕсли;
	
	ОбновитьВидимость();
	
	ГруппаОбученияПриИзмененииНаСервере();
	      	
КонецПроцедуры

&НаКлиенте
Процедура ГруппаОбученияПриИзменении(Элемент)
	
	ГруппаОбученияПриИзмененииНаСервере();
	
	ОбновитьВидимость();
	
КонецПроцедуры
Процедура ГруппаОбученияПриИзмененииНаСервере()
	
	Элементы.Календарь.ВыделенныеДаты.Очистить();	
	
	Если ЗначениеЗаполнено(ЭтотОбъект.ГруппаОбучения) Тогда
		
		Если ЭтотОбъект.ГруппаОбучения.ПН Тогда
			ДобавитьВСписок(1,"Календарь");	
		КонецЕсли;
		Если ЭтотОбъект.ГруппаОбучения.ВТ Тогда
			ДобавитьВСписок(2,"Календарь");	
		КонецЕсли;  
		Если ЭтотОбъект.ГруппаОбучения.СР Тогда
			ДобавитьВСписок(3,"Календарь");	
		КонецЕсли; 
		Если ЭтотОбъект.ГруппаОбучения.ЧТ Тогда
			ДобавитьВСписок(4,"Календарь");	
		КонецЕсли;
		Если ЭтотОбъект.ГруппаОбучения.ПТ Тогда
			ДобавитьВСписок(5,"Календарь");	
		КонецЕсли;
		Если ЭтотОбъект.ГруппаОбучения.СБ Тогда
			ДобавитьВСписок(6,"Календарь");	
		КонецЕсли;
		Если ЭтотОбъект.ГруппаОбучения.ВС Тогда
			ДобавитьВСписок(7,"Календарь");	
		КонецЕсли;
		
		Если ДобавлениеВСуществующиеЗанятия Тогда
			Ученики.Очистить();
			
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

Процедура ДобавитьВСписок(ДеньНедели,Календ) 	
	
	//Если ПродлениеГруппы Тогда		
		ДатаНач 	= ТекущаяДата();
		ДатаКонец 	= КонецМесяца(ДатаНач); 
		Пока ДатаНач <= ДатаКонец Цикл
			Если ДеньНедели(ДатаНач) = ДеньНедели Тогда
				Элементы[Календ].ВыделенныеДаты.Добавить(НачалоДня(ДатаНач));
			КонецЕсли;
			ДатаНач = ДатаНач +86400;
		КонецЦикла;
		
	//Иначе
	//	
	//	ДатаНач 	= ТекущаяДата();
	//	ДатаКонец 	= КонецМесяца(ДатаНач); 
	//	Пока ДатаНач <= ДатаКонец Цикл
	//		Если ДеньНедели(ДатаНач) = ДеньНедели Тогда
	//			Элементы[Календ].ВыделенныеДаты.Добавить(НачалоДня(ДатаНач));
	//		КонецЕсли;
	//		ДатаНач = ДатаНач +86400;
	//	КонецЦикла;
	//КонецЕсли;
	
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
	
	Если ЗаполнятьИзГруппыОбучения Тогда 
		Элементы.Помещение.Доступность 			= Ложь;
		Элементы.Педагог.Доступность 			= Ложь;
		Элементы.ПредметОбучения.Доступность 	= Ложь;
		Элементы.ВремяНачала.Доступность 		= Ложь;
		Элементы.КоличествоЧасов.Доступность 	= Ложь;
	Иначе
		Элементы.Помещение.Доступность 			= Истина;
		Элементы.Педагог.Доступность 			= Истина;
		Элементы.ПредметОбучения.Доступность 	= Истина;
	КонецЕсли;
	
	ОбновитьВидимостьНаСервере();
		
КонецПроцедуры

Процедура ОбновитьВидимостьНаСервере()
	
	Если ЗаполнятьИзГруппыОбучения Тогда 
		ВремяНачала 	= ГруппаОбучения.Время;
		КоличествоЧасов = ГруппаОбучения.Продолжительность;
		Педагог			= ГруппаОбучения.Педагог;
		Помещение		= ГруппаОбучения.Помещение;
		ПредметОбучения	= ГруппаОбучения.ПредметОбучения;
	КонецЕсли;

КонецПроцедуры        

&НаКлиенте
Процедура ПриОткрытии(Отказ)
	Элементы.ИнформационнаяТЗ.Видимость = Ложь;
	
	ГруппаОбученияПриИзмененииНаСервере();
	
	ОбновитьВидимость();
КонецПроцедуры

&НаКлиенте
Процедура ИзГруппыОбученияПриИзменении(Элемент)
	ИзГруппыОбученияПриИзмененииНаСервере();
КонецПроцедуры
Процедура ИзГруппыОбученияПриИзмененииНаСервере()
	
	Элементы.Календарь.ВыделенныеДаты.Очистить();
	
	Если ЗначениеЗаполнено(ЭтотОбъект.ИзГруппыОбучения) Тогда
		Если ЭтотОбъект.ИзГруппыОбучения.ПН Тогда
			ДобавитьВСписок(1,"Календарь");	
		КонецЕсли;
		Если ЭтотОбъект.ИзГруппыОбучения.ВТ Тогда
			ДобавитьВСписок(2,"Календарь");	
		КонецЕсли;  
		Если ЭтотОбъект.ИзГруппыОбучения.СР Тогда
			ДобавитьВСписок(3,"Календарь");	
		КонецЕсли; 
		Если ЭтотОбъект.ИзГруппыОбучения.ЧТ Тогда
			ДобавитьВСписок(4,"Календарь");	
		КонецЕсли;
		Если ЭтотОбъект.ИзГруппыОбучения.ПТ Тогда
			ДобавитьВСписок(5,"Календарь");	
		КонецЕсли;
		Если ЭтотОбъект.ИзГруппыОбучения.СБ Тогда
			ДобавитьВСписок(6,"Календарь");	
		КонецЕсли;
		Если ЭтотОбъект.ИзГруппыОбучения.ВС Тогда
			ДобавитьВСписок(7,"Календарь");	
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
		ПараметрыСтроки.Вставить("Фамилия",Лев(Назв,Симв1-1));
		Назв = СокрЛП(Сред(Назв,Симв1+1));
	Иначе
		ПараметрыСтроки.Вставить("Фамилия",Назв);
		Назв = "";
	КонецЕсли;
	          	
	Если (Найти(Назв," ") > 0) и (СтрДлина(Назв) > 0) Тогда
		Симв2 = Найти(Назв," ");
		ПараметрыСтроки.Вставить("Имя",Лев(Назв,Симв2-1));
		Назв = СокрЛП(Сред(Назв,Симв2+1));
	Иначе
		ПараметрыСтроки.Вставить("Имя",Назв);
		Назв = "";
	КонецЕсли;
	                        	
	Если СтрДлина(Назв) > 0 Тогда
		ПараметрыСтроки.Вставить("Отчество",Назв);
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
	
	Для Каждого Стр из Элементы.Календарь.ВыделенныеДаты Цикл
		
		ВремяЗанятия = ВремяНачала;
		КолЧасов = КоличествоЧасов;
		
		Если ЗаполнятьИзГруппыОбучения Тогда
			ВремяЗанятия 	= ПолучитьВремяИзГруппыОбучения(Стр);
			КолЧасов 		= ГруппаОбучения.Продолжительность;
		КонецЕсли;
		
		Если ЗаполнятьИзГруппыОбучения Тогда
			ПредмОбуч 	= ГруппаОбучения.ПредметОбучения;
			//Пом		 	= ГруппаОбучения.Помещение;
			Пед		 	= ГруппаОбучения.Педагог;
		Иначе
			ПредмОбуч 	= ПредметОбучения;
			//Пом 		= Помещение;
			Пед 		= Педагог;
		КонецЕсли;
		
		
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
		|	И Урок.Дата >= &ДатаНачала
		|	И Урок.Педагог = &Педагог
		//|	И Урок.Помещение = &Помещение
		|	И Урок.ПредметОбучения = &ПредметОбучения";			
		
		//Запрос.УстановитьПараметр("ГруппаОбучения", ГруппаОбучения);
		Запрос.УстановитьПараметр("ПредметОбучения", ПредмОбуч);
		Запрос.УстановитьПараметр("Педагог", Пед);
		//Запрос.УстановитьПараметр("Помещение", Пом);
		Запрос.УстановитьПараметр("ДатаНачала", Стр-('00010101'-ВремяЗанятия)); 
		Запрос.УстановитьПараметр("ДатаОкончания", Стр-('00010101'-ВремяЗанятия)-('00010101'-КолЧасов));        
		
		РезультатЗапроса = Запрос.Выполнить();				
		ВыборкаДетальныеЗаписи = РезультатЗапроса.Выбрать();
		
		Пока ВыборкаДетальныеЗаписи.Следующий() Цикл 					
			НовДок = НайденныеДокументы.Добавить();
			НовДок.Документ 			= ВыборкаДетальныеЗаписи.Ссылка;
			НовДок.ВремяНачала 			= ВыборкаДетальныеЗаписи.Ссылка.Дата;
			НовДок.ВремяОкончания 		= ВыборкаДетальныеЗаписи.Ссылка.Окончание;
			НовДок.Продолжительность 	= ВыборкаДетальныеЗаписи.Ссылка.КоличествоЧасов;
			НовДок.ГруппаОбучения 		= ВыборкаДетальныеЗаписи.Ссылка.ГруппаОбучения;
		КонецЦикла;				
		
	КонецЦикла;
	
КонецПроцедуры

&НаКлиенте
Процедура НайтиДокументы(Команда) 	
	НайденныеДокументы.Очистить();	
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
	
	//ГруппаОбученияПриИзмененииНаСервере();
	
	ОбновитьВидимость();
	
КонецПроцедуры