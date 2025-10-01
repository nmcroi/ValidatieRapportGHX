<cfparam name="FORM.projectPath" default="">
<cfset projectDir = FORM.projectPath>
<cfset setupScript = projectDir & "/setup.sh">
<cfset result = "">
<cfset fouten = "">

<cfif fileExists(setupScript)>
    <cfexecute name="/bin/bash"
               arguments="#setupScript#"
               variable="result"
               errorVariable="fouten"
               timeout="120">
    </cfexecute>

    <cfif len(fouten) EQ 0>
        <cfoutput>
            <p><strong>Setup succesvol uitgevoerd.</strong></p>
            <pre>#htmlEditFormat(result)#</pre>
            <p><a href="validatiePL/setup.log" target="_blank">Bekijk het volledige logbestand</a></p>
        </cfoutput>
    <cfelse>
        <cfoutput>
            <p><strong>FOUT bij uitvoeren van setup.sh:</strong></p>
            <pre>#htmlEditFormat(fouten)#</pre>
        </cfoutput>
    </cfif>
<cfelse>
    <cfoutput>
        <p>setup.sh niet gevonden in map: #setupScript#</p>
    </cfoutput>
</cfif>
