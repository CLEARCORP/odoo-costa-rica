<html>
    <head>
         <style type="text/css">
             ${css}

             .list_table .act_as_row {
                  margin-top: 10px;
                  margin-bottom: 10px;
                  font-size:10px;
             }

             .account_line {
                  font-weight: bold;
                  font-size: 15px;
                  background-color:#F0F0F0;
             }
             
             .account_line .act_as_cell {
                  height: 30px;
                  vertical-align: bottom;
             }

         </style>
    </head>
<body class = "data">
    %for partner in objects :
        <%
            account_types = ['payable','receivable']
                        
            setLang(user.context_lang)
        %>
        </br></br>
        <div style="font-size: 20px; font-weight: bold; text-align: center;"> ${company.partner_id.name | entity} - ${company.currency_id.name | entity}</div>
        <div style="font-size: 25px; font-weight: bold; text-align: center;"> Estado de Cuenta</div>
        <div style="font-size: 20px; font-weight: bold; text-align: center;"> ${partner.name}</div>
        %for account_type in account_types :
            <%
                part_by_curr = get_partners_by_curr(cr, uid, partner, account_type)
                total_balance = 0.0            
            %>
            </br></br>
            %if account_type == 'payable':
                <div style="font-size: 20px; font-weight: bold;"> ${_('PAYABLE')}</div>
            %elif account_type == 'receivable':
                <div style="font-size: 20px; font-weight: bold;"> ${_('RECEIVABLE')}</div>
            %endif
            %for currency in part_by_curr:
                <%
                total_debit_curr = 0.0
                total_credit_curr = 0.0
                total_balance_curr = 0.0
                balance_curr = 0.0
                %>
                %if currency[0] != None:
                      <div class="account_title bg" style="margin-top: 20px; font-size: 12px; width: 1080px;">${_('Partner Balance in ')} ${currency[0]}</div>
                %else:
                      <div class="account_title bg" style="margin-top: 20px; font-size: 12px; width: 1080px;">${_('Partner Balance in ')} ${company.currency_id.name}</div>
                %endif
                <div class="act_as_table list_table">
                <div class="act_as_thead">
              <div class="act_as_row labels" style="font-weight: bold; font-size: 11x;">
                   <div class="act_as_cell first_column" style="vertical-align: middle">${_('Date')}</div>
                   <div class="act_as_cell">${_('Date maturity')}</div>
                   <div class="act_as_cell">${_('Number')}</div>
                   <div class="act_as_cell" style="width: 250px;  vertical-align: middle">${_('Detail')}</div>
                   <div class="act_as_cell amount">${_('Credit')}</div>
                   <div class="act_as_cell amount">${_('Debit')}</div>
              </div>
                </div>
              
                   <div class="act_as_tbody">        
                      %for move_line in sorted(currency[1], key=lambda currency: currency.date):
                   <div class="act_as_row lines">            
                                      ## Date
                                      <div class="act_as_cell first_column">${move_line.date or '0'}</div>
                                      ## Due date
                                      <div class="act_as_cell">${move_line.date_maturity or '-'}</div>
                                      ## Name Move
                                      <div class="act_as_cell">${move_line.move_id.name or '-'}</div>
                                      ## Detail
                                      <div class="act_as_cell" style="width: 250px;  vertical-align: middle">${move_line.name or '-'}</div>
                  %if currency[0] != None:
                      %if move_line.amount_currency > 0: 
                                ## Receivables
                                <div class="act_as_cell amount">${formatLang(move_line.amount_currency) or '0'}</div>
                                ## Payments
                                <div class="act_as_cell amount">${'0.00'}</div>
                                <%total_debit_curr += move_line.amount_currency%>
                      %else:
                                ## Receivables
                                <div class="act_as_cell amount">${'0.00'}</div>
                                ## Payments
                                <div class="act_as_cell amount">${formatLang(move_line.amount_currency*-1) or '0'}</div>
                                <%total_credit_curr += move_line.amount_currency*-1%>
                      %endif
                  %else:
                      ## Payments
                      <div class="act_as_cell amount">${formatLang(move_line.debit) or '0'}</div>
                      ## Receivables
                      <div class="act_as_cell amount">${formatLang(move_line.credit) or '0'}</div>
                      <%
                     ## Totales por Moneda
                     total_debit_curr += move_line.debit
                     total_credit_curr += move_line.credit 
                      %>
                  %endif
                           </div>
                      %endfor
           </div>
           <%
                ## Totales
                total_balance_curr = total_debit_curr - total_credit_curr
                if currency[0] != None:
                      balance_curr = currency_convert(cr, uid, move_line.currency_id.id, company.currency_id.id, total_balance_curr)
                else:
                      balance_curr = total_balance_curr
                endif

                total_balance += balance_curr
           %>
           <div class="act_as_tfoot">
           <div class="act_as_row labels"  style="font-weight: bold; font-size: 11px;" >
                <div class="act_as_cell first_column" style="vertical-align: middle">${_('Balance')}</div>
                %if currency[0] != None:
                      <div class="act_as_cell" style="width: 250px;  vertical-align: middle">${move_line.currency_id.symbol} ${formatLang(total_balance_curr)}</div>
                      <div class="act_as_cell">${_('')}</div>
                      <div class="act_as_cell">${_('')}</div>
                      <div class="act_as_cell amount">${move_line.currency_id.symbol} ${formatLang(total_debit_curr)}</div>
                      <div class="act_as_cell amount">${move_line.currency_id.symbol} ${formatLang(total_credit_curr)}</div>
                %else:
                      <div class="act_as_cell" style="width: 250px;  vertical-align: middle">${company.currency_id.symbol} ${formatLang(total_balance_curr)}</div>
                      <div class="act_as_cell">${_('')}</div>
                      <div class="act_as_cell">${_('')}</div>
                      <div class="act_as_cell amount">${company.currency_id.symbol} ${formatLang(total_debit_curr)}</div>
                      <div class="act_as_cell amount">${company.currency_id.symbol} ${formatLang(total_credit_curr)}</div>
                %endif
                
           </div>
                  </div>
                  </div>
                                   
            %endfor
         
         %if part_by_curr != []:
            <div class="act_as_table list_table " style="margin-top: 20px;">
                 <div class="act_as_tfoot">
                <div class="act_as_row labels"  style="font-weight: bold; font-size: 11px;">
                    <div class="act_as_cell first_column" style="width: 205px; font-size: 12px; text-align: left">${_('TOTAL BALANCE in ')} ${company.currency_id.name}</div>
                    <div class="act_as_cell" style="text-align: left">${company.currency_id.symbol} ${formatLang(total_balance)}</div>
                </div>
                 </div>
            </div>
            <div>
                  <%
                      today = get_time_today()
                      if currency[0] != None:
                           conversion_rate = get_conversion_rate(cr, uid, move_line.currency_id, company.currency_id)
                      else:
                           from_currency = get_currency(cr, uid, 2)
                           conversion_rate = get_conversion_rate(cr, uid, from_currency, company.currency_id)
                      endif
                  %>
            </div>
         %else:
             <div class="account_title bg" style="margin-top: 20px; font-size: 14px; width: 1080px;">${_('There is no open invoices')}</div>
         %endif
        
        %endfor

    </br></br>
    <div style="font-family: Helvetica, Arial; font-size: 13px; font-weight: bold; margin-top: 20px;"> ${_('Note: ')} </div>
    <div style="font-family: Helvetica, Arial; font-size: 12px;"> ${_('In the event of any foreign currencies the Total Balance was calculated according to the exchange rate of the day ')} ${formatLang( today, date=True)} (${company.currency_id.symbol} ${conversion_rate})</div>
    <p style="page-break-after:always"></p>
    
    %endfor    
    
</body>
</html>
