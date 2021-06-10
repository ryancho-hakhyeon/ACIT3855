import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://lab-acit3855.eastus.cloudapp.azure.com/processing/stats`)
            .then(res => res.json())
            .then((result)=>{
                console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
        const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
        return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats Test</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Crawling Image</th>
							<th>List Category</th>
						</tr>
						<tr>
							<td># CI: {stats['num_ci_readings']}</td>
							<td># CL: {stats['num_cl_readings']}</td>
						</tr>
						<tr>
							<td colspan="2">Image Name: {stats['image_name']}</td>
						</tr>
						<tr>
							<td colspan="2">Category Name: {stats['category_name']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
