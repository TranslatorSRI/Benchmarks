import React from "react";
import styles from './Sidebar.module.scss';
import {
  Accordion,
  AccordionItem,
  AccordionItemHeading,
  AccordionItemButton,
  AccordionItemPanel,
} from 'react-accessible-accordion';
import Checkbox from "../Checkbox/Checkbox";
import { capitalizeFirstLetter } from "../../Utilities/utilities";

const Sidebar = ({links, handleLinkClick = (link)=>console.log(link), handleShowBenchmarks}) => {

  return (
    <div className={styles.sidebar}>
      <h5>Recent Benchmarks</h5>
      {
        links &&
        <Accordion
          allowZeroExpanded={true}
          className={styles.accordion}
          >
          {          
            Object.keys(links).map((key, i)=>{
              return(
                <AccordionItem key={i} className={styles.accordionItem}>
                  <AccordionItemHeading className={styles.accordionHeading}>
                    <AccordionItemButton className={styles.accordionButton}>
                      {capitalizeFirstLetter(key)}
                    </AccordionItemButton>
                  </AccordionItemHeading>
                  <AccordionItemPanel className={styles.accordionPanel}>
                    {
                      links[key] &&
                      <Accordion
                        allowMultipleExpanded={true}
                        allowZeroExpanded={true}
                        className={`${styles.accordion}`}
                        >
                        {
                          Object.keys(links[key]).map((key2, j) => {
                            return (
                              <AccordionItem key={j}>
                                <AccordionItemHeading className={styles.accordionHeading}>
                                  <AccordionItemButton className={styles.accordionButton}>
                                    {capitalizeFirstLetter(key2)}
                                  </AccordionItemButton>
                                </AccordionItemHeading>
                                <AccordionItemPanel className={`${styles.accordionPanel} ${styles.checkboxes}`}>
                                  {
                                    links[key][key2] && 
                                    Object.entries(links[key][key2]).map(([i, value], k) => {
                                      return(
                                        <Checkbox 
                                          key={k}
                                          handleClick={(value)=>handleLinkClick(value)}
                                          value={{benchmark:key, ara:key2, timestamp: value}}
                                          >
                                            {value.substring(0,10).replaceAll('-', ' ')}
                                        </Checkbox>
                                      );
                                    })
                                  }
                                </AccordionItemPanel>
                              </AccordionItem>
                            );
                          })
                        }
                      </Accordion>  
                    }
                  </AccordionItemPanel>
                </AccordionItem>
              );
            })  
          }
        </Accordion>
      }
      <button onClick={handleShowBenchmarks} >Show Selected Benchmarks</button>
    </div>
  )
};

export default Sidebar;